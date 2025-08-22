import os
from openai import OpenAI

from llm_services import OpenAIService


class MoonShotAILLMConfig:
    KIMI_K2 = "kimi-k2-0711-preview"
    MAX_OUTPUT_TOKENS_FOR_KIMI_K2 = 16384


class MoonShotAIService(OpenAIService):

    def __init__(self, api_key: str = os.getenv("MOONSHOTAI_API_KEY")):
        super().__init__(api_key)

    def _initialize_client(self, api_key: str):
        return OpenAI(api_key=api_key, base_url="https://api.moonshot.ai/v1")