from llm_services import LLMServiceBase, LLMConfig
from prompts.providers import PromptProvider
from utils.query_executors import (
    QueryExecutor,
)
from utils.schema_loaders import (
    SchemaLoader,
)


class QueryAiAnalyst:
    def __init__(
        self,
        schema_loader: SchemaLoader,
        query_executor: QueryExecutor,
        prompt_provider: PromptProvider,
        llm_service: LLMServiceBase,
        llm_config: LLMConfig,
    ):
        self.schema_loader = schema_loader
        self.query_executor = query_executor
        self.prompt_provider = prompt_provider

        self.llm_service = llm_service
        self.llm_config = llm_config

    def select_relevant_tables(self, user_question):
        all_tables = [a["Name"] for a in self.schema_loader.list_tables()]
        prompt_dto = self.prompt_provider.get_table_selection_prompt()
        if not prompt_dto:
            return all_tables
        return all_tables

    def llm_analytics_query(self, kwargs):
        try:
            prompt_dto = self.prompt_provider.get_construct_sql_prompt(
                cache=self.llm_config.cached,
                user_question=kwargs["user_question"],
                sql_create_table_query=kwargs["sql_create_table_query"],
            )
            response_dict, tokens_usage = self.llm_service.get_function_call_response(
                system_prompt=prompt_dto.system_prompt,
                prompt=prompt_dto.user_prompt,
                function_definition=prompt_dto.get_function_schema(),
                max_tokens=self.llm_config.max_tokens,
                model=self.llm_config.model,
                cached=self.llm_config.cached
            )
            return {
                "analytics_query_output": {
                    "sql_query": response_dict.get("BigQuery_query"),
                    "sql_query_explanation": response_dict.get(
                        "BigQuery_query_explanation"
                    ),
                    "data_limitation_information": response_dict.get(
                        "data_limitation_information", ""
                    ),
                    "response_for_completely_irrelevant_query": response_dict.get(
                        "response_for_completely_irrelevant_query", ""
                    ),
                }
            }
        except Exception as e:
            print(f"Error in llm_analytics_query function: {e}")
            return {}

    def construct_query(self, user_question, activities):
        sql_create_table_query = self.schema_loader.get_create_table_schemas(
            activities,
        )
        output = self.llm_analytics_query(
            {
                "user_question": user_question,
                "sql_create_table_query": sql_create_table_query,
            }
        )
        return output.get("analytics_query_output", {})

    def fetch_data(self, sql_query):
        # print(sql_query)
        return self.query_executor.execute(sql_query)
