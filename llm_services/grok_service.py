import json
import os
from typing import Optional, Dict, Any, List, Tuple

from openai import OpenAI, APIError

from llm_services.llm_service import LLMServiceBase


class GrokLLMConfig:
    GROK_4 = "grok-4-0709"
    GROK_TURBO = "grok-turbo-2024-11-14"
    MAX_OUTPUT_TOKENS_FOR_GROK_4 = 32768
    MAX_OUTPUT_TOKENS_FOR_GROK_TURBO = 32768


class GrokService(LLMServiceBase):
    """
    Service for interacting with xAI's Grok models.
    Uses OpenAI SDK with custom base URL since xAI API is OpenAI-compatible.
    """

    def __init__(self, api_key: str = os.getenv("XAI_API_KEY")):
        super().__init__(api_key)

    def _initialize_client(self, api_key: str):
        # xAI API is OpenAI-compatible, so we use OpenAI client with custom base URL
        return OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )

    def _initialize_async_client(self, api_key: str):
        pass

    def get_stream_response(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        system_prompt: Optional[str] = None,
        cached: bool = False,
    ):
        messages = self._create_messages(prompt, system_prompt)
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in response:
            if (
                chunk.choices
                and chunk.choices[0].delta is not None
                and hasattr(chunk.choices[0].delta, "content")
                and chunk.choices[0].delta.content
            ):
                yield chunk.choices[0].delta.content

    def get_function_call_response(
        self,
        prompt: str | List[Dict[str, Any]],
        model: str,
        max_tokens: int,
        function_definition: Dict,
        system_prompt: Optional[str] = None,
        cached: bool = False,
    ) -> Dict[str, Any]:
        messages = self._create_messages(
            prompt=prompt, system_prompt=system_prompt
        )
        # Convert function definition format if needed
        function_definition = self._convert_function_definition_if_needed(
            function_definition
        )
        tools = [{"type": "function", "function": function_definition}]

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                max_tokens=max_tokens,
                tool_choice="required",
            )
            return self._extract_function_call_arguments(response)
        except APIError as e:
            if "invalid_model" in str(e):
                raise ValueError(f"Invalid model name: {model}") from e
            raise
        except Exception as e:
            print(f"Error in get_function_call_response: {e}")
            raise

    def get_response(
        self,
        prompt: str | List[Dict[str, Any]] | Any,
        model: str,
        max_tokens: int,
        system_prompt: Optional[str] = None,
        cached: bool = False,
    ):
        messages = self._create_messages(prompt, system_prompt)
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
            )
            result = response.choices[0].message.content
            return result, self._get_token_usage(response=response)
        except APIError as e:
            if "invalid_model" in str(e):
                raise ValueError(f"Invalid model name: {model}") from e
            raise
        except Exception as e:
            print(f"Error in get_response: {e}")
            raise

    @staticmethod
    def _extract_function_call_arguments(response):
        try:
            response_dict_str = (
                response.choices[0].message.tool_calls[0].function.arguments
            )
            return json.loads(response_dict_str)
        except Exception as e:
            print(f"Error extracting function call arguments: {e}")
            return {}

    @staticmethod
    def _convert_function_definition_if_needed(
        function_definition: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Convert from Anthropic format to OpenAI format if needed
        definition = function_definition.copy()
        
        # Change the key from "input_schema" to "parameters" if present
        if "input_schema" in definition:
            definition["parameters"] = definition.pop("input_schema")
        
        return definition

    def get_images_llm_message_content(self, images_data, prompt):
        # Note: Grok 4 vision capabilities are coming soon according to docs
        message_content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image_data['image_type']};base64,{image_data['image_data']}",
                    "detail": "auto",
                },
            }
            for image_data in images_data
        ]
        message_content.append({"type": "text", "text": prompt})
        
        return message_content

    def get_pdfs_llm_message_content(self, pdfs_data, prompt):
        # PDF support may not be available yet for Grok
        raise NotImplementedError(
            "PDF processing is not yet supported for Grok models. "
            "Vision and document capabilities are coming soon."
        )

    def get_audios_llm_message_content(
        self, audios_data: List[str], prompt: str
    ):
        # Audio support not available for Grok
        raise NotImplementedError(
            "Audio processing is not supported for Grok models."
        )

    async def get_function_call_response_async(self, prompt: (
            str | List[Dict[str, Any]]
    ), model: str, max_tokens: int, function_definition: Dict, system_prompt: Optional[str] = None,
                                               cached: bool = False) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raise NotImplemented

    @staticmethod
    def _get_token_usage(response) -> Dict:
        usage = getattr(response, 'usage', {})
        return {
            "input_tokens": getattr(usage, 'input_tokens', 0),
            "output_tokens": getattr(usage, 'output_tokens', 0),
            "cached_tokens": getattr(usage, 'cached_tokens', 0)
        }