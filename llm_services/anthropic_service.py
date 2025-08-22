import os
from typing import Optional, Dict, Any, List, Tuple

from anthropic import Anthropic, APIError, NotGiven, AsyncAnthropic
from anthropic.types import ToolUseBlock

from llm_services.llm_service import LLMServiceBase


class AnthropicLLMConfig:
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"
    CLAUDE_4_0_SONNET = "claude-sonnet-4-20250514"
    MAX_OUTPUT_TOKENS_FOR_HAIKU = 4096
    MAX_OUTPUT_TOKENS_FOR_SONNET_3_5 = 8192
    MAX_OUTPUT_TOKENS_FOR_SONNET_3_7 = 64000
    MAX_OUTPUT_TOKENS_FOR_HAIKU_3_5 = 8192
    MAX_OUTPUT_TOKENS_FOR_SONNET_4_0 = 64000


class AnthropicService(LLMServiceBase):
    def __init__(
        self, api_key: Optional[str] = os.environ.get("ANTHROPIC_API_KEY")
    ):
        super().__init__(api_key)

    def _initialize_client(self, api_key: str):
        return Anthropic(api_key=api_key)

    def _initialize_async_client(self, api_key: str):
        return AsyncAnthropic(api_key=api_key)

    def get_function_call_response(
        self,
        prompt: str | List[Dict[str, Any]],
        model: str,
        max_tokens: int,
        function_definition: Dict,
        system_prompt: Optional[str] = NotGiven(),
        cached: bool = False,
    ) -> Tuple[Dict[str, Any], Dict]:
        try:
            messages = self._create_messages(
                prompt=prompt, system_prompt=system_prompt
            )
            extra_headers = None
            if cached:
                extra_headers = {"anthropic-beta": "prompt-caching-2024-07-31"}

            tools = [function_definition]
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
                tools=tools,
                tool_choice={"type": "tool", "name": tools[0]["name"]},
                extra_headers=extra_headers,
            )

            result = self._extract_function_call_arguments_from_llm_response(
                response
            )
            return result, self._get_token_usage(response=response)
        except APIError as e:
            if "invalid_model" in str(e):
                raise ValueError(f"Invalid model name: {model}") from e
            raise
        except Exception as e:
            print(f"Error in get_function_call_response: {e}")
            raise

    async def get_function_call_response_async(
        self,
        prompt: (
                str | List[Dict[str, Any]]
        ),
        model: str,
        max_tokens: int,
        function_definition: Dict,
        system_prompt: Optional[str] = NotGiven(),
        cached: bool = False
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        try:
            messages = [{"role": "user", "content": prompt}]
            tools = [function_definition]
            extra_headers = None
            if cached:
                extra_headers = {"anthropic-beta": "prompt-caching-2024-07-31"}
            response = await self.async_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
                tools=tools,
                system=system_prompt,
                tool_choice={"type": "tool", "name": tools[0]["name"]},
                extra_headers=extra_headers
            )
            result = self._extract_function_call_arguments_from_llm_response(
                response
            )
            return result, self._get_token_usage(response=response)
        except APIError as e:
            if "invalid_model" in str(e):
                raise ValueError(f"Invalid model name: {model}") from e
            raise

    def get_stream_response(
        self,
        prompt: Any,
        model: str,
        max_tokens: int,
        system_prompt: Optional[str] = NotGiven(),
        cached: bool = False,
    ):
        try:
            messages = self._create_messages(prompt=prompt)
            extra_headers = None
            if cached:
                extra_headers = {"anthropic-beta": "prompt-caching-2024-07-31"}
            with self.client.messages.stream(
                system=system_prompt,
                model=model,
                max_tokens=max_tokens,
                messages=messages,
                extra_headers=extra_headers,
            ) as stream:
                for text in stream.text_stream:
                    yield text
                # print(stream.get_final_message())
        except APIError as e:
            if "invalid_model" in str(e):
                raise ValueError(f"Invalid model name: {model}") from e
            raise
        except Exception as e:
            print(f"Error in get_stream_response_using_cache: {e}")
            raise

    def get_response(
        self,
        prompt: str | List[Dict[str, Any]] | Any,
        model: str,
        max_tokens: int,
        system_prompt: Optional[str] = NotGiven(),
        cached: bool = False,
    ):
        try:
            messages = self._create_messages(prompt=prompt)
            extra_headers = None
            if cached:
                extra_headers = {"anthropic-beta": "prompt-caching-2024-07-31"}
            response = self.client.messages.create(
                system=system_prompt,
                model=model,
                max_tokens=max_tokens,
                messages=messages,
                extra_headers=extra_headers,
            )

            result = response.content[0].text
            return result, self._get_token_usage(response=response)
        except APIError as e:
            if "invalid_model" in str(e):
                raise ValueError(f"Invalid model name: {model}") from e
            raise
        except Exception as e:
            print(f"Error in get_response_using_cache: {e}")
            raise

    @staticmethod
    def _extract_function_call_arguments_from_llm_response(response):
        try:
            for content in response.content:
                if isinstance(content, ToolUseBlock):
                    return content.input
            raise ValueError(
                "Failed to extract function call arguments from LLM response"
            )
        except Exception as e:
            print(e)
            return {}

    def get_images_llm_message_content(self, images_data, prompt):
        message_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_data["image_type"],
                    "data": image_data["image_data"],
                },
            }
            for image_data in images_data
        ]
        message_content.append({"type": "text", "text": prompt})

        return message_content

    def get_pdfs_llm_message_content(self, pdfs_data, prompt):
        message_content = [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": pdf_data,
                },
            }
            for pdf_data in pdfs_data
        ]
        message_content.append({"type": "text", "text": prompt})

        return message_content

    def get_audios_llm_message_content(
        self, audios_data: List[str], prompt: str
    ):
        # Use Part.from_data for audio
        raise NotImplementedError

    @staticmethod
    def _get_token_usage(response) -> Dict:
        usage = getattr(response, 'usage', {})
        return {
            "input_tokens": getattr(usage, 'prompt_tokens', 0),
            "output_tokens": getattr(usage, 'completion_tokens', 0),
            "cached_tokens": getattr(usage, 'cached_tokens', 0)
        }