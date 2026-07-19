"""Self-reflection over completed experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.ai.memory import AIMemory


@dataclass(frozen=True)
class Reflection:
    worked: list[str]
    failed: list[str]
    why: str
    lessons: list[str]


class ReflectionEngine:
    """Converts experiment outcomes into durable, queryable lessons."""

    def __init__(self, memory: AIMemory) -> None:
        self.memory = memory

    def reflect(self, result: dict[str, Any]) -> Reflection:
        score = float(result.get("score", 0.0))
        worked = ["Risk-adjusted performance exceeded the baseline"] if score > 0 else []
        failed = [] if score > 0 else ["Risk-adjusted performance did not exceed the baseline"]
        why = "Positive composite research score." if score > 0 else "Composite research score was non-positive."
        lessons = ["Promote the strongest contributing signals"] if score > 0 else ["Avoid repeating this experiment signature without a changed premise"]
        reflection = Reflection(worked, failed, why, lessons)
        self.memory.add("reflection", {"result_id": result.get("experiment_id", "unknown"), "worked": worked, "failed": failed, "why": why, "lessons": lessons})
        return reflection
