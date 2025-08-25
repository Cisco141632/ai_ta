from abc import ABC, abstractmethod

class SchemaLoader(ABC):
    @abstractmethod
    def list_tables(self):
        pass

    @abstractmethod
    def get_create_table_schemas(
        self, table_names, **kwargs
    ):
        pass
