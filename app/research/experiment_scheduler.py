"""Deduplicating priority queue for research experiments."""

from __future__ import annotations

import heapq
from itertools import count
from typing import Any


class ExperimentScheduler:
    """Orders work by importance adjusted for expected resource cost."""

    def __init__(self) -> None:
        self._queue: list[tuple[float, int, str, dict[str, Any]]] = []
        self._ids: set[str] = set()
        self._counter = count()

    def queue(self, experiment_id: str, *, priority: int = 1, cost: float = 1.0, expected_value: float = 0.0, payload: dict[str, Any] | None = None) -> bool:
        if not experiment_id or experiment_id in self._ids:
            return False
        if cost <= 0:
            raise ValueError("Experiment cost must be positive")
        item = {"id": experiment_id, "priority": priority, "cost": cost, "expected_value": expected_value, "payload": payload or {}}
        score = priority + expected_value - (cost * 0.01)
        heapq.heappush(self._queue, (-score, next(self._counter), experiment_id, item))
        self._ids.add(experiment_id)
        return True

    def next_batch(self, limit: int = 1) -> list[dict[str, Any]]:
        if limit < 0:
            raise ValueError("limit cannot be negative")
        batch: list[dict[str, Any]] = []
        while self._queue and len(batch) < limit:
            _, _, experiment_id, item = heapq.heappop(self._queue)
            self._ids.remove(experiment_id)
            batch.append(item)
        return batch

    def __len__(self) -> int:
        return len(self._queue)
