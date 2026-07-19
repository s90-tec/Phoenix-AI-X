from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

from app.ai.memory.models import MemoryRecord


class JSONMemoryStorage:
    """Persist memory records to disk."""

    def __init__(self, storage_path: str | Path) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if self.storage_path.exists():
            self._records = json.loads(self.storage_path.read_text(encoding="utf-8"))
        else:
            self._records: List[dict[str, Any]] = []

    def save(self, record: MemoryRecord) -> None:
        self._records.append(record.__dict__)
        self.storage_path.write_text(json.dumps(self._records, indent=2), encoding="utf-8")

    def load(self) -> List[MemoryRecord]:
        return [MemoryRecord(**item) for item in self._records]
