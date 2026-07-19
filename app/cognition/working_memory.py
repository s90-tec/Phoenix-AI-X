"""Bounded temporary state for a reasoning cycle."""

from __future__ import annotations

from typing import Any


class WorkingMemory:
    """Stores current goals, market state, experiments, tasks, and risks."""

    def __init__(self) -> None:
        self._state: dict[str, Any] = {"current_goals": [], "market_state": {}, "recent_experiments": [], "open_tasks": [], "pending_risks": []}

    def set(self, key: str, value: Any) -> None:
        self._state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def snapshot(self) -> dict[str, Any]:
        return dict(self._state)
