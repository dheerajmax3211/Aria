from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    success: bool
    message: str
    data: Any = None
    task_id: str = ""


class BaseAgent(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    async def execute(self, task: str, context: dict) -> AgentResult:
        pass

    async def rollback(self, task_id: str):
        pass
