"""Append-only research leaderboard."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable


class RankingEngine:
    """Ranks research artifacts while retaining every historic observation."""

    def __init__(self, scoring_function: Callable[[dict[str, Any]], float] | None = None) -> None:
        self.scoring_function = scoring_function or (lambda result: float(result.get("score", 0.0)))
        self._history: dict[str, list[dict[str, Any]]] = {}

    def update(self, item_id: str, result: dict[str, Any]) -> dict[str, Any]:
        entry = {"item_id": item_id, "score": self.scoring_function(result), "result": dict(result), "timestamp": datetime.now(timezone.utc).isoformat()}
        self._history.setdefault(item_id, []).append(entry)
        return entry

    def leaderboard(self, limit: int | None = None) -> list[dict[str, Any]]:
        current = [entries[-1] for entries in self._history.values()]
        ranked = sorted(current, key=lambda item: item["score"], reverse=True)
        return ranked if limit is None else ranked[:limit]

    def history(self, item_id: str) -> list[dict[str, Any]]:
        return list(self._history.get(item_id, []))
