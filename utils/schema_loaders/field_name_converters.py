import copy

column_types_mapping = {
    "RADIO_GROUP": "VARCHAR(255)",
    "DROPDOWN": "VARCHAR(255)",
    "TIME": "TIME",
    "DATE": "DATE",
    "LONG_TEXT": "TEXT",
    "URL": "VARCHAR(255)",
    "MULTI_SELECT": "TEXT",
    "INTEGER": "INT",
    "DATE_TIME": "DATETIME",
    "PLAIN_TEXT": "VARCHAR(100)",
    "EMAIL": "VARCHAR(255)",
    "PHONE_NUMBER": "VARCHAR(20)",
    "FIELDS_SELECTOR": "TEXT",
    "FLOAT": "FLOAT",
}


class FKRelation:
    def __init__(self, target_table, target_col):
        self.target_table = target_table
        self.target_col = target_col

    @property
    def table(self):
        return self.target_table

    @property
    def col(self):
        return self.target_col


class Column:
    def __init__(
        self,
        col_name,
        col_type,
        is_pk=False,
        fk_relation=None,
        col_id=None,
        allowed_values="",
        description=None,
    ):
        self.name = col_name
        self.type = col_type
        self.is_pk = is_pk
        self.fk_relation = fk_relation
        self.col_id = col_id
        self.allowed_values = allowed_values
        self.description = description

    @property
    def fk(self):
        return self.fk_relation

    def get_allowed_values(self):
        if self.allowed_values:
            return f"-- Possible values: {self.allowed_values}"
        return ""

    def get_description(self):
        if self.description:
            return f"-- Description: {self.description}"
        return ""


class Table:
    def __init__(self, table_name, columns, table_id=None):
        self.name = table_name
        self.columns = [copy.deepcopy(col) for col in columns]
        self.table_id = table_id
        self._col_id_mapping = {c.col_id: c for c in self.columns}
        self._col_name_mapping = {c.name: c for c in self.columns}

    def get_col_names(self):
        return [col.name for col in self.columns]

    def get_pk(self):
        for col in self.columns:
            if col.is_pk:
                return col
        return None

    def get_fk_columns(self):
        return [col for col in self.columns if col.fk_relation]

    def add_col(self, col: Column):
        self.columns.append(copy.deepcopy(col))
        self._col_name_mapping[col.name] = col
        self._col_id_mapping[col.col_id] = col

    def get_col_from_name(self, name):
        return self._col_name_mapping.get(name)

    def get_col_from_id(self, col_id):
        return self._col_id_mapping.get(col_id)

    def get_create_table_query(self, col_suffix=""):
        query = f"CREATE TABLE {self.name} (\n"
        for col in self.columns:
            if col.is_pk:
                query += f"\t{col.name}{col_suffix} {col.type} PRIMARY KEY, {col.get_description()}\n"
            else:
                query += f"\t{col.name}{col_suffix} {col.type}, {col.get_description()} {col.get_allowed_values()}\n"
        for col in self.get_fk_columns():
            query += f"\tFOREIGN KEY ({col.name}{col_suffix}) REFERENCES {col.fk.table}({col.fk.col}{col_suffix}),\n"
        query = query[:-2] + "\n);"
        return query

    def translate_query_to_col_ids(self, sql_query, col_suffix=""):
        col_name_id_mapping = {
            v.name: k for k, v in self._col_id_mapping.items()
        }
        for k in sorted(
            col_name_id_mapping.keys(), reverse=True, key=lambda x: len(x)
        ):
            sql_query = sql_query.replace(
                k + col_suffix, col_name_id_mapping[k]
            )
        return sql_query.replace(f"`{self.name}`", f"`{self.table_id}`")


class FieldNameConverter:
    def __init__(
        self,
        fields_mapping=None,
        table_ids_mapping=None,
        nested_fields=None,
        value_mapping=None,
    ):
        self.fields_mapping = fields_mapping
        self.table_ids_mapping = table_ids_mapping
        self.tables = []
        self.tables_mapping = dict()
        self.nested_fields_list = nested_fields
        self.value_mapping = value_mapping

    def get_table_names(self):
        return [t.name for t in self.tables]

    @staticmethod
    def convert_name_into_valid_sql(name):
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

    def initialize(self):
        tables = []
        if self.nested_fields_list:
            for table in self.nested_fields_list:
                table_name = self.convert_name_into_valid_sql(
                    table["Table Name"]
                )
                table_id = table["Table Name"]
                columns = []
                for field in table["fields"]:
                    is_pk = field.get("is_primary_key", False)
                    col_name = self.convert_name_into_valid_sql(
                        field["field_name"]
                    )
                    col_type = column_types_mapping[field["field_type"]]
                    col_id = field["field_id"]
                    col_allowed_values = field.get("options")
                    field_description = field.get("field_description")
                    if (
                        col_name in self.value_mapping
                        and not col_allowed_values
                    ):
                        col_allowed_values = list(
                            self.value_mapping[col_name].values()
                        )
                    column = Column(
                        col_name,
                        col_type,
                        is_pk=is_pk,
                        col_id=col_id,
                        allowed_values=col_allowed_values,
                        description=field_description,
                    )
                    if field.get("fk_config"):
                        reference_table_name = (
                            self.convert_name_into_valid_sql(
                                field["fk_config"]["table_name"]
                            )
                        )
                        reference_col_name = self.convert_name_into_valid_sql(
                            field["fk_config"]["field_name"]
                        )
                        column.fk_relation = FKRelation(
                            reference_table_name, reference_col_name
                        )
                    columns.append(column)

                table = Table(table_name, columns, table_id=table_id)
                tables.append(table)
            for table in tables:
                table_name = table.name
                self.tables.append(table)
                self.tables_mapping[table_name] = table

        else:
            self.create_table_objs()

    def create_table_objs(self):
        tables_dict = {}
        table_ids_dict = {}
        for k, v in self.fields_mapping.items():
            is_pk = False
            table, field = k.split(">")
            table_id = self.table_ids_mapping[table.strip()]
            table, field = (
                self.convert_name_into_valid_sql(table),
                field.strip(),
            )
            col, col_type = field.split("|")
            col, col_type = (
                self.convert_name_into_valid_sql(col),
                column_types_mapping[col_type.strip()],
            )
            table_ids_dict[table] = table_id
            if tables_dict.get(table):
                tables_dict[table].append(
                    Column(col, col_type, is_pk, col_id=v)
                )
            else:
                tables_dict[table] = [Column(col, col_type, is_pk, col_id=v)]

        for table_name in tables_dict.keys():
            table = Table(
                table_name,
                tables_dict[table_name],
                table_id=table_ids_dict[table_name],
            )
            self.tables.append(table)
            self.tables_mapping[table_name] = table

    def get_create_table_queries(self):
        return [table.get_create_table_query() for table in self.tables]

    def get_table(self, table_name):
        return self.tables_mapping[table_name]
