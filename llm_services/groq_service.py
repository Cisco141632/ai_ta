import os
from typing import Optional, Dict, Any, List, Tuple

from groq import Groq

from llm_services.llm_service import LLMServiceBase


class GroqLLMConfig:
    LLAMA_3_1_70B_VERSATILE = "llama-3.1-70b-versatile"
    KIMI_K2_INSTRUCT = "moonshotai/kimi-k2-instruct"
    MAX_OUTPUT_TOKENS_FOR_LLAMA_3_1_70B_VERSATILE = 4096
    MAX_OUTPUT_TOKENS_FOR_KIMI_K2_INSTRUCT = 16384


class GroqService(LLMServiceBase):

    def __init__(
        self, api_key: Optional[str] = os.environ.get("GROQ_API_KEY")
    ):
        super().__init__(api_key)

    def _initialize_client(self, api_key: str):
        return Groq(api_key=api_key)

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
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def get_response(
        self,
        prompt: str | List[Dict[str, Any]] | Any,
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
        )
        result = response.choices[0].message.content
        return result, self._get_token_usage(response=response)

    def get_function_call_response(
        self,
        prompt: str | List[Dict[str, Any]],
        model: str,
        max_tokens: int,
        function_definition: Dict,
        system_prompt: Optional[str] = None,
        cached: bool = False,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def get_pdfs_llm_message_content(self, pdfs_data, prompt):
        raise NotImplementedError

    def get_audios_llm_message_content(
        self, audios_data: List[str], prompt: str
    ):
        # Use Part.from_data for audio
        raise NotImplementedError

    async def get_function_call_response_async(self, prompt: (
            str | List[Dict[str, Any]]
    ), model: str, max_tokens: int, function_definition: Dict, system_prompt: Optional[str] = None,
                                               cached: bool = False) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raise NotImplementedError



    def get_images_llm_message_content(self, images_data, prompt):
        raise NotImplementedError

    @staticmethod
    def _get_token_usage(response) -> Dict:
        usage = response.usage
        return {
            "input_tokens": getattr(usage, 'prompt_tokens', 0),
            "output_tokens": getattr(usage, 'completion_tokens', 0),
            "cached_tokens": getattr(usage, 'cached_tokens', 0)
        }