import base64
import json
import os
from io import BytesIO
from typing import Optional, Dict, Any, List, Tuple

from openai import OpenAI, APIError, AsyncOpenAI

from llm_services.llm_service import LLMServiceBase


class OpenAILLMConfig:
    GPT_4_1 = "gpt-4.1-2025-04-14"
    GPT_4_O = "gpt-4o-2024-08-06"
    GPT_4_O_MINI = "gpt-4o-mini-2024-07-18"
    GPT_O_3_MINI = "o3-mini"
    MAX_OUTPUT_TOKENS_FOR_GPT_4_O = 16384
    MAX_OUTPUT_TOKENS_FOR_GPT_4_1 = 32768
    MAX_OUTPUT_TOKENS_FOR_GPT_4_O_MINI = 16384
    MAX_OUTPUT_TOKENS_FOR_GPT_O_3_MINI = 100000


class OpenAIService(LLMServiceBase):

    def __init__(self, api_key: str = os.getenv("OPENAI_API_KEY")):
        super().__init__(api_key)

    def _initialize_client(self, api_key: str):
        return OpenAI(api_key=api_key)

    def _initialize_async_client(self, api_key: str):
        return AsyncOpenAI(api_key=api_key)

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
            # More robust check for delta and content to avoid AttributeError
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
    ) -> Tuple[Dict[str, Any], Dict]:
        messages = self._create_messages(
            prompt=prompt, system_prompt=system_prompt
        )
        function_definition = (
            self._convert_function_definition_from_anthropic_to_openai(
                function_definition
            )
        )
        tools = [{"type": "function", "function": function_definition}]

        try:
            if model in [OpenAILLMConfig.GPT_O_3_MINI]:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=tools,
                    max_completion_tokens=max_tokens,
                    tool_choice="required",
                )
            else:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=tools,
                    max_tokens=max_tokens,
                    tool_choice="required",
                )
            result = self._extract_function_call_arguments(response)
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
        function_definition: Dict,
        model: str,
        max_tokens: int,
        system_prompt: Optional[str] = None,
        cached: bool = False
    ):
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
            function_definition = (
                self._convert_function_definition_from_anthropic_to_openai(
                    function_definition
                )
            )
            tools = [{"type": "function", "function": function_definition}]
            try:
                if model in (
                        OpenAILLMConfig.GPT_O_3_MINI
                ):
                    response = await self.async_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        tools=tools,
                        tool_choice="required",
                    )
                else:
                    response = await self.async_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        tools=tools,
                        max_completion_tokens=max_tokens,
                        tool_choice="required",
                    )
                result = self._extract_function_call_arguments(response)
                return result, self._get_token_usage(response=response)
            except APIError as e:
                if "invalid_model" in str(e):
                    raise ValueError(f"Invalid model name: {model}") from e
                raise
            except Exception as e:
                print(f"Error in get_function_call_response: {e}")
                raise
        except APIError as e:
            if "invalid_model" in str(e):
                raise ValueError(f"Invalid model name: {model}") from e
            raise
        except Exception as e:
            print(e)
            return {}

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
            if model in [OpenAILLMConfig.GPT_O_3_MINI]:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                )
            else:
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
    def _convert_function_definition_from_anthropic_to_openai(
        anthropic_function: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Create a copy of the Claude definition
        gpt_definition = anthropic_function.copy()

        # Change the key from "input_schema" to "parameters"
        if "input_schema" in gpt_definition:
            gpt_definition["parameters"] = gpt_definition.pop("input_schema")

        return gpt_definition

    def get_images_llm_message_content(self, images_data, prompt):
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
        message_content = []
        for pdf_data in pdfs_data:
            file_id = self.upload_pdf_file(pdf_data=pdf_data)
            message_content.append({
                "type": "file",  # ✅ correct this line
                "file": {
                    "file_id": file_id
                }
            })
        message_content.append({"type": "text", "text": prompt})

        return message_content

    def upload_pdf_file(self, pdf_data: bytes) -> str:
        try:
            pdf_bytes = base64.b64decode(pdf_data)
            file_like = BytesIO(pdf_bytes)
            file_like.name = "document.pdf"  # Important for OpenAI to accept the file

            file_response = self.client.files.create(
                file=file_like,
                purpose="user_data"
            )
            return file_response.id
        except Exception as e:
            print(f"Error uploading PDF file: {e}")
            raise

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