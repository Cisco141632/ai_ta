import os
from typing import Optional, Dict, Any, List, Tuple

import google.generativeai as genai
from google.generativeai.types.generation_types import GenerationConfig
from proto.marshal.collections import RepeatedComposite

from llm_services.llm_service import LLMServiceBase


class GeminiLLMConfig:
    GEMINI_1_5_PRO = "models/gemini-1.5-pro"
    GEMINI_1_5_FLASH = "models/gemini-1.5-flash"
    GEMINI_2_0_FLASH = "models/gemini-2.0-flash"
    GEMINI_2_5_PRO = "models/gemini-2.5-pro"
    GEMINI_2_5_FLASH_LITE = "models/gemini-2.5-flash-lite"
    MAX_OUTPUT_TOKENS_FOR_GEMINI_1_5_PRO = 8192
    MAX_OUTPUT_TOKENS_FOR_GEMINI_1_5_FLASH = 8192
    MAX_OUTPUT_TOKENS_FOR_GEMINI_2_0_FLASH = 8192
    MAX_OUTPUT_TOKENS_FOR_GEMINI_2_5_PRO = 8192
    MAX_OUTPUT_TOKENS_FOR_GEMINI_2_5_FLASH_LITE = 8192


class GeminiService(LLMServiceBase):

    def __init__(
        self, api_key: Optional[str] = os.environ.get("GOOGLE_API_KEY")
    ):
        super().__init__(api_key)

    def _initialize_client(self, api_key: str):
        genai.configure(api_key=api_key)
        return genai

    def _initialize_async_client(self, api_key: str):
        self._initialize_client(api_key=api_key)

    def get_stream_response(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        system_prompt: Optional[str] = None,
        cached: bool = False,
    ):
        try:
            model = self.client.GenerativeModel(
                model_name=model, system_instruction=system_prompt
            )
            response = model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    max_output_tokens=max_tokens
                ),
                stream=True,
            )
            for chunk in response:
                yield chunk.text
        except ValueError as e:
            if "model not found" in str(e).lower():
                raise ValueError(f"Invalid model name: {model}") from e
            raise
        except Exception as e:
            print(f"Error in get_stream_response: {e}")
            raise

    def get_response(
            self,
            prompt: str | List[Dict[str, Any]] | Any,
            model: str,
            max_tokens: int,
            system_prompt: Optional[str] = None,
            cached: bool = False,
    ):
        try:
            # Prepare arguments for the GenerativeModel constructor
            model_kwargs = {
                'model_name': model
            }

            # Check if a system prompt is provided
            if system_prompt:
                # Check if the model is a Gemma model, which doesn't support system_instruction
                if "gemma" in model.lower():
                    # Workaround: Prepend the system prompt to the user prompt
                    # This only works reliably for string prompts.
                    if isinstance(prompt, str):
                        prompt = f"{system_prompt}\n\n---\n\n{prompt}"
                    else:
                        # For chat history (list of dicts), this simple workaround is not ideal.
                        # A proper implementation would insert a new message at the start.
                        # For now, we'll log a warning or raise an error if this combination is used.
                        print("Warning: System prompts for Gemma models are best used with simple string prompts.")
                        # You could also raise an error:
                        # raise ValueError("System prompts with Gemma models only supported for string prompts in this implementation.")
                else:
                    # For non-Gemma models (like Gemini), use the dedicated parameter
                    model_kwargs['system_instruction'] = system_prompt

            # Initialize the model with the correct arguments
            model_instance = self.client.GenerativeModel(**model_kwargs)

            # --- END OF FIX ---

            response = model_instance.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    max_output_tokens=max_tokens
                ),
            )
            result = response.text
            return result, self._get_token_usage(response=response)
        except ValueError as e:
            if "model not found" in str(e).lower():
                raise ValueError(f"Invalid model name: {model}") from e
            raise
        except Exception as e:
            # The original error message will be printed here
            print(f"Error in get_response: {e}")
            raise

    def get_function_call_response(
        self,
        prompt: str | List[Dict[str, Any]],
        model: str,
        max_tokens: int,
        function_definition: Dict,
        system_prompt: Optional[str] = None,
        cached: bool = False,
    ) -> Tuple[Dict[str, Any], Dict]:
        try:
            # Convert function definition to Gemini format
            gemini_function = self._convert_function_definition_to_gemini(
                function_definition
            )

            # Initialize model with the function
            model = self.client.GenerativeModel(
                model_name=model,
                tools=[gemini_function],
                generation_config=GenerationConfig(
                    max_output_tokens=max_tokens
                ),
            )

            # Configure function calling
            tool_config = {
                "function_calling_config": {
                    "mode": "ANY",
                    "allowed_function_names": [function_definition["name"]],
                }
            }

            # Get response
            response = model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    max_output_tokens=max_tokens
                ),
                tool_config=tool_config,
            )

            # Extract and parse function call arguments
            function_response = None
            for part in response.candidates[0].content.parts:
                if hasattr(part, "function_call"):
                    args = part.function_call.args
                    # Parse the protobuf structure into a clean dictionary
                    result = {}
                    # print(f"Args: {args.__dict__}")
                    for key, value in args.items():
                        # print(f"value: {value}, key: {key}")
                        result[key] = self._parse_gemini_value(value)
                    # print(f"Result: {result}")
                    function_response = result
                    break
            if not function_response:
                raise ValueError("No function call found in response")
            return function_response, self._get_token_usage(response=response)

        except ValueError as e:
            if "model not found" in str(e).lower():
                raise ValueError(f"Invalid model name: {model}") from e
            raise
        except Exception as e:
            print(f"Error in get_function_call_response: {e}")
            raise


    async def get_function_call_response_async(
        self,
        prompt: (
                str | List[Dict[str, Any] | str]
        ),
        model: str,
        max_tokens: int,
        function_definition: Dict,
        system_prompt: Optional[str] = None,
        cached: bool = False
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        try:
            # Convert function definition to Gemini format
            gemini_function = self._convert_function_definition_to_gemini(function_definition)

            # Initialize model with the function
            model = self.client.GenerativeModel(
                model_name=model,
                tools=[gemini_function],
                generation_config=GenerationConfig(
                    max_output_tokens=max_tokens
                ),
                system_instruction=system_prompt
            )

            # Configure function calling
            tool_config = {
                "function_calling_config": {
                    "mode": "ANY",
                    "allowed_function_names": [function_definition["name"]]
                }
            }

            # Get response
            response = await model.generate_content_async(
                prompt,
                generation_config=GenerationConfig(max_output_tokens=max_tokens),
                tool_config=tool_config
            )

            # Extract and parse function call arguments
            # print(response)
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call'):
                    args = part.function_call.args
                    # Parse the protobuf structure into a clean dictionary
                    result = {}
                    # print(f"Args: {args.__dict__}")
                    for key, value in args.items():
                        # print(f"value: {value}, key: {key}")
                        result[key] = self._parse_gemini_value(value)
                    # print(f"Result: {result}")
                    return result, self._get_token_usage(response=response)

            raise ValueError("No function call found in response")

        except ValueError as e:
            if "model not found" in str(e).lower():
                raise ValueError(f"Invalid model name: {model}") from e
            raise
        except Exception as e:
            print(f"Error in get_function_call_response: {e}")
            raise

    @staticmethod
    def _convert_function_definition_to_gemini(
        function_definition: Dict,
    ) -> Dict:
        """Convert function definition to Gemini's expected format."""

        def _convert_type(type_str: str) -> str:
            """Convert OpenAPI/Anthropic types to Gemini types."""
            type_mapping = {
                "object": "OBJECT",
                "string": "STRING",
                "integer": "INTEGER",
                "number": "NUMBER",
                "boolean": "BOOLEAN",
                "array": "ARRAY",
            }
            return type_mapping.get(type_str, type_str.upper())

        def _convert_schema(schema: Dict) -> Dict:
            """Recursively convert schema to Gemini format."""
            converted = {}

            if "type" in schema:
                converted["type_"] = _convert_type(schema["type"])

            if "properties" in schema:
                converted["properties"] = {
                    key: _convert_schema(value)
                    for key, value in schema["properties"].items()
                }

            if "items" in schema:
                converted["items"] = _convert_schema(schema["items"])

            if "required" in schema:
                converted["required"] = schema["required"]

            if "enum" in schema:
                converted["enum"] = schema["enum"]

            if "description" in schema:
                converted["description"] = schema["description"]

            # print(f"{converted}: converted")
            return converted

        # Create base function definition
        gemini_function = {
            "name": function_definition["name"],
            "description": function_definition.get("description", ""),
            "parameters": _convert_schema(function_definition["input_schema"]),
        }

        return gemini_function

    def _parse_gemini_value(self, value):
        """Parse Gemini response value into Python native types."""
        if isinstance(value, RepeatedComposite):
            return [self._parse_struct_value(v) for v in value]
        elif isinstance(value, str):
            # print(f"str: {value}")
            return value
        elif isinstance(value, float):
            return value
        else:
            # print(value)
            return self._parse_struct_value(value)

    def _parse_struct_value(self, struct):
        """Parse Gemini struct value into a dictionary."""
        # print(f"Struct: {struct}")
        # print(f"type of struct: {type(struct)}")
        # print(f"Struct: {struct.__dict__}")
        if isinstance(struct, RepeatedComposite):
            result = []
            for v in struct:
                result.append(self._parse_gemini_value(v))
            return result
        elif isinstance(struct, str):
            # print(f"str: {struct}")
            return struct
        else:
            result = {}
            for key, value in struct.items():
                # print(f"value: {value}, key: {key}")
                result[key] = self._parse_gemini_value(value)
            return result

    def get_images_llm_message_content(self, images_data, prompt):

        message_content = [
            {
                "mime_type": image_data["image_type"],
                "data": image_data["image_data"],
            }
            for image_data in images_data
        ]
        message_content.append(
            prompt,
        )

        return message_content

    def get_pdfs_llm_message_content(self, pdfs_data, prompt):
        message_content = [
            {
                "mime_type": pdf_data["pdf_type"],
                "data": pdf_data["pdf_data"],
            }
            for pdf_data in pdfs_data
        ]
        message_content.append(
            prompt,
        )

        return message_content

    def get_audios_llm_message_content(
        self, audios_data: List[str], prompt: str
    ):
        # Use Part.from_data for audio
        raise NotImplementedError

    @staticmethod
    def _get_token_usage(response) -> Dict:
        usage = getattr(response, 'usage_metadata', {})
        return {
            "input_tokens": getattr(usage, 'prompt_token_count', 0),
            "output_tokens": getattr(usage, 'candidates_token_count', 0),
            "cached_tokens": getattr(usage, 'cached_content_token_count', 0)
        }