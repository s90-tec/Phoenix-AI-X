from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from app.ai.memory.models import MemoryRecord
from app.ai.memory.repositories import MemoryRepository
from app.ai.memory.storage import JSONMemoryStorage


class AIMemory:
    """High-level memory facade for agents and kernel."""

    def __init__(self, storage_path: str | Path | None = None) -> None:
        storage = JSONMemoryStorage(storage_path or Path("memory") / "ai_memory.json")
        self.repository = MemoryRepository(storage=storage)

    def add(self, category: str, content: Dict[str, Any], metadata: Dict[str, Any] | None = None) -> MemoryRecord:
        record = MemoryRecord(category=category, content=content, metadata=metadata or {})
        self.repository.add(record)
        return record

    def list(self, category: str | None = None) -> List[MemoryRecord]:
        records = self.repository.list()
        if category is None:
            return records
        return [record for record in records if record.category == category]
