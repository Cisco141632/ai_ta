import csv
import json
from collections import defaultdict
from typing import Dict, List, Any, Optional

class ColumnTypeMapper:
    @staticmethod
    def get_mapping() -> Dict[str, str]:
        return {
            "PLAIN_TEXT": "PLAIN_TEXT",
            "RADIO_GROUP": "RADIO_GROUP",
            "DROPDOWN": "DROPDOWN",
            "TIME": "TIME",
            "Date": "DATE",
            "LONG_TEXT": "LONG_TEXT",
            "URL": "URL",
            "MULTI_SELECT": "MULTI_SELECT",
            "INTEGER": "INTEGER",
            "FLOAT": "FLOAT",
            "DATE_TIME": "DATE_TIME",
            "EMAIL": "EMAIL",
            "PHONE_NUMBER": "PHONE_NUMBER",
            "FIELDS_SELECTOR": "FIELDS_SELECTOR",
        }


class CSVReader:
    @staticmethod
    def read_csv(file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile, skipinitialspace=True)
            return [row for row in reader if any(row.values())]


class TableSchemaBuilder:
    def __init__(
        self,
        fields_data: List[Dict[str, Any]],
        tables_data: List[Dict[str, Any]],
    ):
        self.fields_data = fields_data
        self.tables_data = tables_data
        self.column_types_mapping = ColumnTypeMapper.get_mapping()

    def _build_table_config_map(self) -> Dict[str, Dict[str, Any]]:
        table_config_map = {}
        for row in self.tables_data:
            if row.get("Considered For Analytics", "") == "Yes":
                table_config_map[row["Analytics TableName"]] = {
                    "description": row.get("Analytics Table Description", ""),
                    "internal_name": row.get("Bigquery ViewName", ""),
                }
        return table_config_map

    def _build_tables_map(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        tables_map = defaultdict(lambda: defaultdict(lambda: {}))
        for row in self.fields_data:
            if row["Should consider for Analytics"] == "Yes":
                table_map = tables_map[row["Analytics TableName"]]
                column_name = (
                    row["Analytic Field Name"].strip()
                )
                column_map = table_map[column_name]

                column_map["Column Type"] = self.column_types_mapping[
                    row["Field Type"]
                ]
                column_map["Allowed Values"] = self._get_allowed_values(row)
                column_map["Column Description"] = row[
                    "Analytic Field Description"
                ]
                column_map["FieldId"] = row.get("FieldId", "")
                column_map["AnalyticsName"] = row["Analytic Field Name"]
                column_map["Is Primary Key"] = row["Is Primary Key"] == "Yes"
                column_map["fk_config"] = self._get_fk_config(row)

        return tables_map

    @staticmethod
    def _get_allowed_values(row: Dict[str, Any]) -> List[str]:
        if row["Field Type"] in [
            "DROPDOWN",
            "FIELDS_SELECTOR",
            "MULTI_SELECT",
            "RADIO_GROUP",
        ]:
            values = [
                item.strip()
                for item in row["Values if Dropdown Field"].split("\n")
            ]
            return values[-50:] if len(values) > 100 else values
        return []

    @staticmethod
    def _get_fk_config(row: Dict[str, Any]) -> Optional[Dict[str, str]]:
        if row["Foreign Key Config"]:
            val = (
                row["Foreign Key Config"]
                .replace("FK ", "")
                .replace("(", "")
                .replace(")", "")
            )
            fk_table_name, fk_field_name = val.split(", ")
            return {"table_name": fk_table_name, "field_name": fk_field_name}
        return None

    def build_schema(self) -> List[Dict[str, Any]]:
        table_config_map = self._build_table_config_map()
        tables_map = self._build_tables_map()

        schema = []
        for table_name, table_data in tables_map.items():
            table_config = table_config_map[table_name]
            table_map = {
                "Table Name": table_name,
                "Table Description": table_config["description"],
                "big_query_table_name": table_config["internal_name"],
                "fields": self._build_columns(table_data),
            }
            schema.append(table_map)

        return schema

    @staticmethod
    def _build_columns(
        table_data: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        columns = []
        for column_name, column_config in table_data.items():
            columns.append(
                {
                    "field_name": column_name,
                    "field_id": column_config.get("FieldId", ""),
                    "field_type": column_config["Column Type"],
                    "options": column_config["Allowed Values"],
                    "field_description": column_config["Column Description"],
                    "is_primary_key": column_config["Is Primary Key"],
                    "fk_config": column_config.get("fk_config"),
                    "bigquery_column_name": column_config.get(
                        "AnalyticsName", ""
                    ),
                }
            )
        return columns


class StageConfigBuilder:
    def __init__(self, stages_data: List[Dict[str, Any]]):
        self.stages_data = stages_data

    def build_stages_config(self) -> Dict[str, List[Dict[str, Any]]]:
        stages_config = {"usual_stages": [], "misc_stage": []}
        for row in self.stages_data:
            formatted_row = {
                "stage_id": row["Stage Id"],
                "name": row["Stage Display Name"],
                "order": int(row["Stage Order"]),
                "description": row["Description"],
                "is_misc": row["Is Misc Stage"],
            }

            if row["Is Misc Stage"] == "No":
                stages_config["usual_stages"].append(formatted_row)
            else:
                stages_config["misc_stage"].append(formatted_row)

        stages_config["usual_stages"].sort(key=lambda x: x["order"])
        stages_config["misc_stage"].sort(key=lambda x: x["order"])
        return stages_config


class SchemaWriter:
    @staticmethod
    def write_json(data: Any, file_path: str) -> None:
        with open(file_path, "w") as writer:
            json.dump(data, writer, indent=2, sort_keys=True)


class SchemaGenerator:
    def __init__(
        self,
        fields_file: str,
        tables_file: str,
        output_json_file: str
    ):
        self.fields_file = fields_file
        self.tables_file = tables_file
        self.output_json_file = output_json_file

    def generate_schema(self) -> None:
        fields_data = CSVReader.read_csv(self.fields_file)
        tables_data = CSVReader.read_csv(self.tables_file)

        table_schema_builder = TableSchemaBuilder(fields_data, tables_data)
        schema = table_schema_builder.build_schema()


        SchemaWriter.write_json(
            data=schema, file_path=self.output_json_file
        )



