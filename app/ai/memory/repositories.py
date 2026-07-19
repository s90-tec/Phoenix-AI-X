from __future__ import annotations

from typing import List

from app.ai.memory.models import MemoryRecord
from app.ai.memory.storage import JSONMemoryStorage


class MemoryRepository:
    """Repository layer for the AI memory system."""

    def __init__(self, storage: JSONMemoryStorage | None = None) -> None:
        self.storage = storage or JSONMemoryStorage("memory/ai_memory.json")

    def add(self, record: MemoryRecord) -> None:
        self.storage.save(record)

    def list(self) -> List[MemoryRecord]:
        return self.storage.load()
