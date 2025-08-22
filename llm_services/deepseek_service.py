import os
from openai import OpenAI

from llm_services import OpenAIService


class DeepSeekLLMConfig:
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_REASONER = "deepseek-reasoner"
    MAX_OUTPUT_TOKENS_FOR_DEEPSEEK_CHAT = 4000
    MAX_OUTPUT_TOKENS_FOR_DEEPSEEK_REASONER = 8000


class DeepSeekService(OpenAIService):

    def __init__(self, api_key: str = os.getenv("DEEPSEEK_API_KEY")):
        super().__init__(api_key)

    def _initialize_client(self, api_key: str):
        return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")