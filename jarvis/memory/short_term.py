from collections import deque
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class ConversationTurn:
    role: str
    content: str


class ShortTermMemory:
    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self.history: deque[ConversationTurn] = deque(maxlen=max_turns)

    def add(self, role: str, content: str):
        self.history.append(ConversationTurn(role=role, content=content))
        logger.debug(f"Short-term memory: added {role} turn ({len(self.history)}/{self.max_turns})")

    def get_history(self) -> list[dict]:
        return [{"role": turn.role, "content": turn.content} for turn in self.history]

    def get_recent(self, n: int = 5) -> list[dict]:
        recent = list(self.history)[-n:]
        return [{"role": turn.role, "content": turn.content} for turn in recent]

    def clear(self):
        self.history.clear()
        logger.info("Short-term memory cleared")

    @property
    def is_empty(self) -> bool:
        return len(self.history) == 0

    @property
    def turn_count(self) -> int:
        return len(self.history)
