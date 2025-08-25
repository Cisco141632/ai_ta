from agents.query_analyzer import QueryAiAnalyst
from utils.data_sets.ecommerce.bigquery import BigQueryEcommerceUploader
from llm_services import LLMConfig
from llm_services.deepseek_service import DeepSeekService, DeepSeekLLMConfig
from prompts.providers.maud import MAUDPromptProvider
from utils.query_executors import BQQueryExecutor
from utils.schema_gen.generate_schema_json import SchemaGenerator
from utils.schema_loaders import DataSchemaLoader

if __name__=="__main__":
    # bq_uploader = BigQueryEcommerceUploader(
    #     project_id="hybrid-dominion-469805-m4",
    #     dataset_id="ecommerce",
    #     credentials_path="/home/dw-dev-009/Downloads/hybrid-dominion-469805-m4-5f3a10493537.json"
    # )
    # bq_uploader.upload_all_data()


    # fields_file_ = "utils/schema_gen/maud/Prod - Data Copilot (Final) - Copilot - Fields Config.csv"
    # tables_file_ = "utils/schema_gen/maud/Prod - Data Copilot (Final) - Copilot - Table Config.csv"
    #
    # schema_generator = SchemaGenerator(
    #     fields_file=fields_file_,
    #     tables_file=tables_file_,
    #     output_json_file="utils/schema_gen/maud/tables.json"
    # )
    # schema_generator.generate_schema()

    user_question = "Authority wise submitted applications"
    q = QueryAiAnalyst(
        schema_loader=DataSchemaLoader(),
        llm_service=DeepSeekService(),
        llm_config=LLMConfig(
            model=DeepSeekLLMConfig.DEEPSEEK_CHAT,
            max_tokens=DeepSeekLLMConfig.MAX_OUTPUT_TOKENS_FOR_DEEPSEEK_CHAT,
            cached=False
        ),
        query_executor=BQQueryExecutor(),
        prompt_provider=MAUDPromptProvider()
    )
    s = q.select_relevant_tables(user_question=user_question)
    p = q.construct_query(user_question=user_question, activities=s)
    print(p)