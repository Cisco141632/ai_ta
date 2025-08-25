import json
import re
from typing import Tuple, Dict, List, Any

import sqlglot

TABLES_JSON_PATH = "utils/schema_loaders/data_schema.json"


class BigQueryTableNameConverterInteractor:
    def __init__(
        self,
        tables_json_path: str = TABLES_JSON_PATH,
    ):
        self.tables_json_path = (
            tables_json_path if tables_json_path else "tables.json"
        )

        table_mapping, field_mapping = self._fetch_required_data_mappings()

        self.table_mapping = table_mapping

    def get_converted_sql_query(
        self, sql_query: str
    ) -> Tuple[str, Dict[str, str]]:
        """
        :param sql_query: A valid sql query
        :return: updated sql query where table names, column names are transformed
        """
        try:
            select_expression = sqlglot.parse_one(
                self.format_sql_query(sql_query)
            )
        except Exception as e:
            print(e)
            return "", {}

        table_names = self._get_table_names_from_select_expression(
            select_expression
        )
        converted_bigquery = self._replace_table_names(
            table_names=table_names, sql_query=sql_query
        )
        return converted_bigquery, {}

    @staticmethod
    def _replace_whole_word(query, old_word, new_word) -> str:
        pattern = r'(?<!["\'])\b' + re.escape(old_word) + r'\b(?!["\'])'
        modified_text = re.sub(pattern, new_word, query)
        return modified_text

    def _replace_table_names(
        self, table_names: List[str], sql_query: str
    ) -> str:
        for table_name in table_names:
            bq_table_name = self.table_mapping.get(table_name)
            if not bq_table_name:
                continue
            sql_query = self._replace_whole_word(
                query=sql_query,
                old_word=f"{table_name}",
                new_word=f"{bq_table_name}",
            )
            sql_query = self._replace_whole_word(
                query=sql_query,
                old_word=f'"{table_name}"',
                new_word=bq_table_name,
            )
            sql_query = self._replace_whole_word(
                query=sql_query,
                old_word=f"`{table_name}`",
                new_word=bq_table_name,
            )
            sql_query = self._replace_whole_word(
                query=sql_query,
                old_word=f"'{table_name}'",
                new_word=bq_table_name,
            )

            sql_query = self._replace_whole_word(
                query=sql_query,
                old_word=f" {table_name} ",
                new_word=f" {bq_table_name} ",
            )
            sql_query = self._replace_whole_word(
                query=sql_query,
                old_word=f" {table_name}",
                new_word=f" {bq_table_name}",
            )
            sql_query = self._replace_whole_word(
                query=sql_query,
                old_word=f" {table_name};",
                new_word=f" {bq_table_name};",
            )

        return sql_query

    @staticmethod
    def _get_table_names_from_select_expression(
        select_expression: sqlglot.expressions.Expression,
    ) -> List[str]:
        return list(
            set(
                [
                    table.this.name
                    for table in list(
                        select_expression.find_all(sqlglot.expressions.Table)
                    )
                ]
            )
        )

    def _fetch_required_data_mappings(
        self,
    ) -> Tuple[Dict[str, str], Dict[str, Dict]]:
        data = self._read_data_from_json_file(file_path=self.tables_json_path)

        table_mapping, field_mapping = {}, {}
        for table_dict in data:
            table_name = table_dict["Table Name"]
            table_name = self._convert_name_into_valid_sql(name=table_name)
            table_mapping[table_name] = (
                f"`{table_dict['big_query_table_name']}`"
            )
            for field_dict in table_dict["fields"]:
                field_dict["bigquery_column_name"] = (
                    f"`{field_dict['bigquery_column_name']}`"
                )
                field_key_ = self._prep_field_mapping_key(
                    field_name=field_dict["field_name"]
                )
                field_mapping[field_key_] = field_dict
        return table_mapping, field_mapping

    @staticmethod
    def _prep_field_mapping_key(field_name: str) -> str:
        return field_name

    @staticmethod
    def format_sql_query(query: str):
        return query.replace("`", "'")

    @classmethod
    def _read_data_from_json_file(cls, file_path: str) -> Any:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        return data

    @staticmethod
    def _convert_name_into_valid_sql(name):
        # return (
        #     "_".join(name.strip().lower().split())
        #     .replace("#", "")
        #     .replace("_&_", "_and_")
        #     .replace("&", "_and_")
        #     .replace("_/_", "_or_")
        #     .replace("/", "_or_")
        #     .replace("-", "_")
        #     .replace(".", "_")
        #     .replace("?", "")
        # )
        return name
