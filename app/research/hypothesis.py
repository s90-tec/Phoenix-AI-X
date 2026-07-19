"""Research hypothesis domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Hypothesis:
    """A falsifiable trading idea awaiting evaluation."""

    description: str
    reasoning: str
    expected_outcome: str
    priority: int = 1
    status: str = "draft"
    confidence: float = 0.5
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Hypothesis description is required")
        if self.priority < 0:
            raise ValueError("Hypothesis priority cannot be negative")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Hypothesis confidence must be between 0 and 1")
