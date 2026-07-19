from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AIContext:
    """Shared context object for agent collaboration."""

    market_state: Dict[str, Any] = field(default_factory=dict)
    portfolio: Dict[str, Any] = field(default_factory=dict)
    risk_metrics: Dict[str, Any] = field(default_factory=dict)
    model_registry: Dict[str, Any] = field(default_factory=dict)
    strategy_registry: Dict[str, Any] = field(default_factory=dict)
    knowledge: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    current_tasks: Dict[str, Any] = field(default_factory=dict)
    agent_results: Dict[str, Any] = field(default_factory=dict)
    event_log: list[Dict[str, Any]] = field(default_factory=list)
    memory: Optional[object] = None

    def add_task(self, task_id: str, payload: Dict[str, Any]) -> None:
        self.current_tasks[task_id] = payload

    def update(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
