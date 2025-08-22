import os

from openai import AzureOpenAI

from llm_services import OpenAIService


class AzureAILLMConfig:
    GPT_4_O = "gpt-4o"
    GPT_4_1 = "gpt-4.1"
    GPT_4_O_MINI = "gpt-4o-mini"
    GPT_O_3_MINI = "o3-mini"
    MAX_OUTPUT_TOKENS_FOR_GPT_4_O = 16384
    MAX_OUTPUT_TOKENS_FOR_GPT_4_1 = 32767
    MAX_OUTPUT_TOKENS_FOR_GPT_4_O_MINI = 16384
    MAX_OUTPUT_TOKENS_FOR_GPT_O_3_MINI = 100000


class AzureAIService(OpenAIService):
    def __init__(self, api_key: str = os.getenv("AzureAI_API_KEY")):
        self.azure_endpoint = (
            "https://ai-admin4758ai655931178171.openai.azure.com/"
        )
        self.api_version = "2024-10-21"
        super().__init__(api_key)

    def _initialize_client(self, api_key: str):
        return AzureOpenAI(
            api_key=api_key,
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint,
        )
