from typing import Optional, List, Dict, Any, Tuple
import os
from llm_services import LLMServiceBase

class OpenRouterLLMConfig:
    GPT_4_1 = "gpt-4.1-2025-04-14"
    QWEN_3_CODER = "qwen/qwen3-coder:free"
    QWEN_3_30B = "qwen/qwen3-30b-a3b:free"
    MAX_OUTPUT_TOKENS_FOR_GPT_4_O = 16384
    MAX_OUTPUT_TOKENS_FOR_QWEN_3_CODER = 16384
    MAX_OUTPUT_TOKENS_FOR_QWEN_3_30B = 16384

class OpenRouterService(LLMServiceBase):

    def _initialize_client(self, api_key: str = os.getenv("OPENROUTER_API_KEY")):
        from openai import OpenAI

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        return client

    def _initialize_async_client(self, api_key: str):
        pass

    def get_pdfs_llm_message_content(self, pdfs_data, prompt):
        raise NotImplemented

    async def get_function_call_response_async(self, prompt: (
            str | List[Dict[str, Any]]
    ), model: str, max_tokens: int, function_definition: Dict, system_prompt: Optional[str] = None,
                                               cached: bool = False) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raise NotImplemented



    def get_audios_llm_message_content(self, audios_data: List[str], prompt: str):
        raise NotImplemented

    def get_function_call_response(
        self, prompt: str | List[Dict[str, Any]],
        model: str,
        max_tokens: int,function_definition: Dict, system_prompt: Optional[str] = None,
        cached: bool = False
    ) -> Dict[str, Any]:
        raise NotImplemented


    def get_images_llm_message_content(self, images_data, prompt):
        raise NotImplemented

    def get_response(self, prompt: str | List[Dict[str, Any]] | Any, model: str, max_tokens: int,
                     system_prompt: Optional[str] = None, cached: bool = False):
        completion = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": f"""{system_prompt}\n\n{prompt}"""
                }
            ],
            max_tokens=8000
        )

        return completion.choices[0].message.content

    def get_stream_response(self, prompt: str, model: str, max_tokens: int, system_prompt: Optional[str] = None,
                            cached: bool = False):
        raise NotImplemented