import base64
import json
import os
from typing import List, Dict, Any, Optional, Tuple

from google import genai
from google.genai.types import (
    HttpOptions,
    FunctionDeclaration,
    GenerateContentConfig,
    Tool,
    Content,
    Part,
    FunctionCallingConfig,
    ToolConfig,
    FunctionCallingConfigMode,
)
from google.oauth2 import service_account

from llm_services import LLMServiceBase


class VERTEXAILLMConfig:
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash-preview-04-17"
    GEMINI_2_5_FLASH_LITE_PREVIEW_06_17 = "gemini-2.5-flash-lite-preview-06-17"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
    GEMINI_2_0_FLASH_LITE_SFT = "889985393452122112"  # Changed to your tuned model ID
    GEMINI_2_5_FLASH_PREVIEW_05_20 = "gemini-2.5-flash-preview-05-20"

    # Add your tuned model IDs from the screenshot
    TUNED_MODEL_1 = "889985393452122112"

    MAX_OUTPUT_TOKENS_FOR_GEMINI_2_5_PRO = 65535
    MAX_OUTPUT_TOKENS_FOR_GEMINI_2_5_FLASH = 65535
    MAX_OUTPUT_TOKENS_FOR_GEMINI_2_5_FLASH_PREVIEW_05_20 = 65535
    MAX_OUTPUT_TOKENS_FOR_GEMINI_2_5_FLASH_LITE_PREVIEW_06_17 = 65535
    MAX_OUTPUT_TOKENS_FOR_GEMINI_2_0_FLASH_LITE = 8192
    MAX_OUTPUT_TOKENS_FOR_GEMINI_2_0_FLASH_LITE_SFT = 8192
    MAX_OUTPUT_TOKENS_FOR_TUNED_MODELS = 8192


VERTEXAI_CREDENTIAL_PATH = os.environ.get("VERTEXAI_CREDENTIAL_PATH")


class VertexAIService(LLMServiceBase):
    def __init__(self, api_key=None):
        self.credentials = (
            service_account.Credentials.from_service_account_file(
                VERTEXAI_CREDENTIAL_PATH,
                scopes=[
                    "https://www.googleapis.com/auth/cloud-platform",
                ],
            )
        )

        super().__init__(api_key)

    @staticmethod
    def _is_tuned_model(model):
        """Check if the model is a tuned model (numeric ID)"""
        tuned_model_ids = [
            VERTEXAILLMConfig.TUNED_MODEL_1
        ]
        return model in tuned_model_ids or model.isdigit()

    @staticmethod
    def _get_location_for_model(model):
        """Determine the correct location based on the model"""
        if model == VERTEXAILLMConfig.GEMINI_2_5_FLASH_LITE_PREVIEW_06_17:
            return "global"
        # Tuned models are typically in us-central1
        return "us-central1"

    def _get_model_path(self, model):
        """Get the correct model path for publisher vs tuned models"""
        if self._is_tuned_model(model):
            # For tuned models, the model parameter should be the endpoint path
            # Format: projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID
            location = self._get_location_for_model(model)
            return f"projects/{self.credentials.project_id}/locations/{location}/endpoints/{model}"
        else:
            # Publisher model - use just the model name
            return model

    def _get_client_for_model(self, model):
        """Get or create a client with the appropriate location for the model"""
        required_location = self._get_location_for_model(model)

        # If we don't have a client or need a different location, create new client
        if (self.client is None or
                getattr(self.client, '_location', None) != required_location):

            client = genai.Client(
                http_options=HttpOptions(api_version="v1"),
                credentials=self.credentials,
                project=self.credentials.project_id,
                location=required_location,
                vertexai=True,
            )
            # Store location for comparison
            client._location = required_location

            # Only update self.client if this is the default location
            if required_location == "us-central1":
                self.client = client

            return client

        return self.client

    def _initialize_client(self, api_key: str):
        # Initialize default client with us-central1
        client = genai.Client(
            http_options=HttpOptions(api_version="v1"),
            credentials=self.credentials,
            project=self.credentials.project_id,
            location="us-central1",
            vertexai=True,
        )
        client._location = "us-central1"
        return client

    def _initialize_async_client(self, api_key: str):
        pass

    @staticmethod
    def _build_contents(prompt, system_prompt=None):
        contents = []
        # System prompt is no longer added here as a content object with role="system"
        # It will be passed separately as system_instructions parameter

        # Handle prompt as list-of-message dicts (for chat/multimodal) or as string
        if isinstance(prompt, list):
            for msg in prompt:
                if isinstance(msg, Content):
                    contents.append(msg)
                else:
                    # Each msg should be a dict with at least 'role' and 'content'
                    role = msg.get("role", "user")
                    # Skip system role messages as they're not supported in content
                    if role == "system":
                        continue
                    content = msg.get("text", "")
                    # If content is already a list of Parts (e.g., for images), use as is
                    if isinstance(content, list) and all(
                            isinstance(p, Part) for p in content
                    ):
                        parts = content
                    else:
                        parts = [Part.from_text(text=content)]
                    contents.append(Content(role=role, parts=parts))
        else:
            contents.append(
                Content(role="user", parts=[Part.from_text(text=prompt)])
            )
        return contents

    @LLMServiceBase.llm_tracker.track_llm_call()
    def get_response(
            self, prompt, model, max_tokens, system_prompt=None, cached=False
    ):
        try:
            # Get the appropriate client for this model
            client = self._get_client_for_model(model)

            # Build contents without including system prompt in the contents
            contents = self._build_contents(prompt)

            # Create config for the generate_content call
            config = GenerateContentConfig(max_output_tokens=max_tokens)

            # Experiment: add system prompt to contents properly
            if system_prompt:
                system_content = Content(
                    parts=[Part.from_text(text=system_prompt)],
                    role="user",  # Using user role since system role isn't supported
                )
                # Insert system prompt at the beginning of contents
                contents.insert(0, system_content)

            # Get the correct model path
            model_path = self._get_model_path(model)

            response = client.models.generate_content(
                model=model_path,  # Use the correct path
                contents=contents,
                config=config,
            )
            # Vertex AI SDK returns text in response.candidates[0].text
            result = response.candidates[0].content.parts[0].text
            return result, self._get_token_usage(response=response)
        except Exception as e:
            print(f"Error in get_response: {e}")
            # Fallback to a known working model if tuned model fails
            if self._is_tuned_model(model):
                print(f"Tuned model {model} failed, falling back to gemini-2.5-flash")
                result = self.get_response(
                    prompt,
                    VERTEXAILLMConfig.GEMINI_2_5_FLASH,
                    max_tokens,
                    system_prompt,
                    cached
                )
                return result
            raise

    @LLMServiceBase.llm_tracker.track_llm_call()
    def get_stream_response(
            self, prompt, model, max_tokens, system_prompt=None, cached=False
    ):
        try:
            # Get the appropriate client for this model
            client = self._get_client_for_model(model)

            # Build contents without including system prompt in the contents
            contents = self._build_contents(prompt)

            # Create config for streaming response
            config = GenerateContentConfig(
                temperature=0, max_output_tokens=max_tokens
            )

            # Experiment: add system prompt to contents properly
            if system_prompt:
                system_content = Content(
                    parts=[Part.from_text(text=system_prompt)],
                    role="user",  # Using user role since system role isn't supported
                )
                # Insert system prompt at the beginning of contents
                contents.insert(0, system_content)

            # Get the correct model path
            model_path = self._get_model_path(model)

            response = client.models.generate_content_stream(
                model=model_path,  # Use the correct path
                contents=contents,
                config=config,
            )
            for chunk in response:
                if hasattr(chunk, "candidates") and chunk.candidates:
                    # Fix: Access content parts correctly
                    if (
                            hasattr(chunk.candidates[0], "content")
                            and chunk.candidates[0].content
                    ):
                        if (
                                hasattr(chunk.candidates[0].content, "parts")
                                and chunk.candidates[0].content.parts
                        ):
                            yield chunk.candidates[0].content.parts[0].text
        except Exception as e:
            print(f"Error in get_stream_response: {e}")
            raise

    @LLMServiceBase.llm_tracker.track_llm_call()
    def get_function_call_response(
            self,
            prompt,
            model,
            max_tokens,
            function_definition,
            system_prompt=None,
            cached: bool = False,
    ):

        try:
            # Get the appropriate client for this model
            client = self._get_client_for_model(model)

            # Build contents without including system prompt in the contents
            contents = self._build_contents(prompt)

            # Convert function definition to VertexAI FunctionDeclaration
            vertexai_function = self._convert_function_definition_to_vertexai(
                function_definition
            )

            # Create config with function calling settings
            tool_config = ToolConfig(
                function_calling_config=FunctionCallingConfig(
                    mode=FunctionCallingConfigMode.ANY,
                )
            )
            config = GenerateContentConfig(
                max_output_tokens=max_tokens,
                tools=[Tool(function_declarations=[vertexai_function])],
                tool_config=tool_config,
            )

            # Experiment: add system prompt to contents properly
            if system_prompt:
                system_content = Content(
                    parts=[Part.from_text(text=system_prompt)],
                    role="user",  # Using user role since system role isn't supported
                )
                # Insert system prompt at the beginning of contents
                contents.insert(0, system_content)

            # Get the correct model path
            model_path = self._get_model_path(model)

            response = client.models.generate_content(
                model=model_path,  # Use the correct path
                contents=contents,
                config=config,
            )

            # Extract function call arguments from response.function_calls
            result = None
            if hasattr(response, "function_calls") and response.function_calls:
                result = response.function_calls[0].args
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and hasattr(
                        candidate.content, "parts"
                ):
                    for part in candidate.content.parts:
                        if (
                                hasattr(part, "function_call")
                                and part.function_call
                        ):
                            result = part.function_call
                            break
            if not result:
                raise ValueError("No function call found in response")
            return result, self._get_token_usage(response=response)
        except Exception as e:
            print(f"Error in get_function_call_response: {e}")
            raise

    @staticmethod
    def _convert_function_definition_to_vertexai(function_definition):
        def _convert_type(type_str):
            type_mapping = {
                "object": "OBJECT",
                "string": "STRING",
                "integer": "INTEGER",
                "number": "NUMBER",
                "boolean": "BOOLEAN",
                "array": "ARRAY",
            }
            return type_mapping.get(type_str.lower(), type_str.upper())

        def _convert_schema(schema):
            converted = {}
            if "type" in schema:
                converted["type"] = _convert_type(schema["type"])
            if "properties" in schema:
                converted["properties"] = {
                    k: _convert_schema(v)
                    for k, v in schema["properties"].items()
                }
            if "items" in schema:
                converted["items"] = _convert_schema(schema["items"])
            if "required" in schema:
                converted["required"] = schema["required"]
            if "enum" in schema:
                converted["enum"] = schema["enum"]
            if "description" in schema:
                converted["description"] = schema["description"]
            return converted

        parameters = _convert_schema(function_definition["input_schema"])

        # check. if parameters is empty, then use input_schema
        with open("function_definition.json", "w") as f:
            json.dump(function_definition["input_schema"], f, indent=4)

        with open("parameters.json", "w") as f:
            json.dump(parameters, f, indent=4)

        return FunctionDeclaration(
            name=function_definition["name"],
            description=function_definition.get("description", ""),
            parameters=parameters,
        )

    @staticmethod
    def _parse_vertexai_value(value):
        # Handles protobuf/struct value parsing
        try:
            from proto.marshal.collections import RepeatedComposite

            if isinstance(value, RepeatedComposite):
                return [
                    VertexAIService._parse_vertexai_value(v) for v in value
                ]
            elif isinstance(value, str):
                return value
            elif isinstance(value, float):
                return value
            elif hasattr(value, "items"):
                return {
                    k: VertexAIService._parse_vertexai_value(v)
                    for k, v in value.items()
                }
            else:
                return value
        except ImportError:
            return value

    def get_images_llm_message_content(self, images_data, prompt):
        # Use Part.from_data for images
        parts = [
            Part.from_bytes(
                data=base64.b64decode(image_data["image_data"]),
                mime_type=image_data["image_type"],
            )
            for image_data in images_data
        ]
        parts.append(Part.from_text(text=prompt))
        return [Content(role="user", parts=parts)]

    def get_pdfs_llm_message_content(self, pdfs_data, prompt):
        # Use Part.from_data for PDFs
        parts = [
            Part.from_bytes(
                data=base64.b64decode(pdf_data), mime_type="application/pdf"
            )
            for pdf_data in pdfs_data
        ]
        parts.append(Part.from_text(text=prompt))
        return [Content(role="user", parts=parts)]

    def get_audios_llm_message_content(
            self, audios_data: List[Dict], prompt: str
    ):
        # Use Part.from_data for audio
        parts = [
            Part.from_bytes(
                data=base64.b64decode(audio_data["audio_data"]),
                mime_type=audio_data["audio_type"],
            )
            for audio_data in audios_data
        ]
        parts.append(Part.from_text(text=prompt))
        return [Content(role="user", parts=parts)]

    async def get_function_call_response_async(self, prompt: (
            str | List[Dict[str, Any]]
    ), model: str, max_tokens: int, function_definition: Dict, system_prompt: Optional[str] = None,
                                               cached: bool = False) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raise NotImplemented



    @staticmethod
    def _get_token_usage(response) -> Dict:
        usage = getattr(response, 'usage_metadata', {})
        input_tokens = getattr(usage, 'prompt_token_count', 0)
        output_tokens = getattr(usage, 'candidates_token_count', 0)
        cached_tokens = getattr(usage, 'cached_content_token_count', 0)
        tokens_usage = {
                "input_tokens": input_tokens if input_tokens else 0,
                "output_tokens": output_tokens if output_tokens else 0,
                "cached_tokens": cached_tokens if cached_tokens else 0
        }
        return tokens_usage
