import json
import os

from .field_name_converters import FieldNameConverter
from .base import SchemaLoader

class DataSchemaLoader(SchemaLoader):
    def __init__(self):
        schema_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data_schema.json"
        )
        with open(schema_file_path) as f:
            self.schema = json.load(f)
        self.converter = FieldNameConverter(
            nested_fields=self.schema,
            value_mapping={},
        )
        self.converter.initialize()

    @property
    def activities_list(self):
        return [
            {
                "Name": a["Table Name"],
                "Description": a["Table Description"],
                "Fields": [f["field_name"] for f in a["fields"]],
            }
            for a in self.schema
        ]

    def list_tables(self):
        return self.activities_list

    def _get_valid_table_names(self, table_names):
        return list(
            map(self.converter.convert_name_into_valid_sql, table_names)
        )

    def get_create_table_schemas(
        self, table_names, **kwargs
    ):
        valid_table_names = self._get_valid_table_names(table_names)
        sql_create_table_query = ""
        for table_name in valid_table_names:
            table = self.converter.get_table(table_name)
            create_table_query = table.get_create_table_query()
            sql_create_table_query += create_table_query + "\n"
        return sql_create_table_query
