"""Attention allocation for competing operational signals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AttentionItem:
    topic: str
    priority: int
    payload: dict[str, Any]


class AttentionSystem:
    """Ranks urgent risks ahead of archival information."""

    WEIGHTS = {"market_crash": 100, "high_volatility": 90, "risk_alert": 95, "model_degradation": 85, "completed_report": 10, "archived_experiment": 5}

    def prioritize(self, items: list[AttentionItem]) -> list[AttentionItem]:
        return sorted(items, key=lambda item: self.WEIGHTS.get(item.topic, 50) + item.priority, reverse=True)
