from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional


@dataclass
class PromptDTO:
    system_prompt: str
    user_prompt: Any
    get_function_schema: Callable[..., Dict]


class PromptProvider(ABC):
    @abstractmethod
    def get_table_selection_prompt(self, **kwargs) -> Optional[PromptDTO]:
        pass

    @abstractmethod
    def get_construct_sql_prompt(self, **kwargs) -> PromptDTO:
        pass

    @abstractmethod
    def get_chart_selection_prompt(self, **kwargs) -> PromptDTO:
        pass

    @staticmethod
    def _from_template(template: str, **kwargs) -> str:
        return template.format(**kwargs)
