from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class Experiment:
    """A single recorded experiment artifact."""

    experiment_id: str
    dataset: str
    features: list[str] = field(default_factory=list)
    strategy: str = ""
    model: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    winner: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "draft"
