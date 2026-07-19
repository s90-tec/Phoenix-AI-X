from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List, Optional


@dataclass
class KnowledgeItem:
    kind: str
    title: str
    summary: str
    tags: List[str] = field(default_factory=list)
    source: str = "unknown"
    confidence: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class KnowledgeBase:
    """Repository for persisted knowledge items."""

    def __init__(self) -> None:
        self._items: List[KnowledgeItem] = []

    def add_item(self, item: KnowledgeItem) -> KnowledgeItem:
        self._items.append(item)
        return item

    def list_items(self, *, kind: Optional[str] = None, tag: Optional[str] = None) -> List[KnowledgeItem]:
        items = self._items
        if kind is not None:
            items = [item for item in items if item.kind == kind]
        if tag is not None:
            items = [item for item in items if tag in item.tags]
        return items
