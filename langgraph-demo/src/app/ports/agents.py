from typing import Any, Protocol


class BaseAgent:
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """This must the the entrypointer for the agentic workflow"""
        ...
