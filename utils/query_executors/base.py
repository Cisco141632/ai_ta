from abc import ABC, abstractmethod


class QueryExecutor(ABC):
    @abstractmethod
    def execute(self, query):
        pass
