from typing import Optional, List, Dict, Any

from .base import PromptProvider, PromptDTO
from ..templates.maud import *


class MAUDPromptProvider(PromptProvider):
    def __init__(self):
        self.tg_bpass_context = BUILDNOW_CONTEXT

    def get_table_selection_prompt(self) -> Optional[PromptDTO]:
        return None

    def get_construct_sql_prompt(
        self, cache: bool, user_question: str, sql_create_table_query: str
    ) -> PromptDTO:
        system_prompt = ANALYTICS_QUERY_SYSTEM_PROMPT
        get_function_schema = lambda: ANALYTICS_QUERY_FUNCTION_SCHEMA
        if cache:
            user_prompt = self._get_user_content_for_construct_sql(
                user_question=user_question,
                sql_create_table_query=sql_create_table_query,
            )
        else:
            user_prompt = self._get_user_prompt(
                user_question=user_question,
                sql_create_table_query=sql_create_table_query
            )
        return PromptDTO(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            get_function_schema=get_function_schema,
        )

    def get_chart_selection_prompt(
        self,
        single_row_dataframe: bool,
        user_question: str,
        sql_query: str,
        dataframe_info: Any,
        dataframe_str: Optional[Any] = None,
    ) -> PromptDTO:
        if single_row_dataframe:
            system_prompt = TEXTUAL_SYSTEM_PROMPT
            user_prompt_template = TEXTUAL_USER_PROMPT
            function_definition = get_analysis_summary_function_schema()
            user_prompt = self._from_template(
                user_prompt_template,
                user_question=user_question,
                sql_query=sql_query,
                dataframe_str=dataframe_str,
            )
        else:
            system_prompt = CHART_SELECTION_MULTIPLE_ROWS_SYSTEM_PROMPT
            user_prompt_template = CHART_SELECTION_MULTIPLE_ROWS_USER_PROMPT
            function_definition = CHART_SELECTION_MULTIPLE_ROWS_FUNCTION_SCHEMA
            user_prompt = self._from_template(
                user_prompt_template,
                user_question=user_question,
                sql_query=sql_query,
                dataframe_info=dataframe_info,
                # example=VEGA_SPEC_EXAMPLE,
                # sample_data = dataframe,
            )
        get_function_schema = lambda: function_definition
        return PromptDTO(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            get_function_schema=get_function_schema,
        )

    def _get_user_content_for_construct_sql(self, **kwargs) -> List[Dict]:
        return [
            {
                "type": "text",
                "text": ANALYTICS_QUERY_USER_PROMPT_CACHE_BREAK_POINT_1.format(
                    business_context=self.tg_bpass_context,
                    sql_create_table_query=kwargs["sql_create_table_query"],
                ),
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": ANALYTICS_QUERY_USER_PROMPT_CACHE_BREAK_POINT_2,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": ANALYTICS_QUERY_USER_PROMPT_CACHE_BREAK_POINT_3.format(
                    user_question=kwargs["user_question"]
                ),
            },
        ]

    def _get_user_prompt(self, **kwargs) -> str:
        part_1 = ANALYTICS_QUERY_USER_PROMPT_CACHE_BREAK_POINT_1.format(
            business_context=self.tg_bpass_context,
            sql_create_table_query=kwargs["sql_create_table_query"],
        )
        part_2 = ANALYTICS_QUERY_USER_PROMPT_CACHE_BREAK_POINT_2
        part_3 = ANALYTICS_QUERY_USER_PROMPT_CACHE_BREAK_POINT_3.format(
            user_question=kwargs["user_question"]
        )
        return f"""
            {part_1}
            {part_2},
            {part_3}
        """
