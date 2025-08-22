import os

from openai import OpenAI

from llm_services import OpenAIService


class LMStudioLLMConfig:
    GPT_OSS_20B = "openai/gpt-oss-20b"
    MAX_OUTPUT_TOKENS_FOR_GPT_OSS_20B = 8000


class LMStudioService(OpenAIService):

    def __init__(self, api_key: str = 'lm-studio'):
        super().__init__(api_key)

    def _initialize_client(self, api_key: str):
        return OpenAI(api_key=api_key, base_url="http://localhost:1234/v1")