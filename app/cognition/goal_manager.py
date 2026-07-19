"""Goal domain model and prioritized repository."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Goal:
    title: str
    priority: int = 1
    progress: float = 0.0
    dependencies: list[str] = field(default_factory=list)
    deadline: str | None = None
    status: str = "active"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Goal title is required")
        if not 0 <= self.progress <= 1:
            raise ValueError("Goal progress must be between 0 and 1")


class GoalManager:
    """Owns active goals and only exposes goals with completed dependencies."""

    def __init__(self) -> None:
        self._goals: dict[str, Goal] = {}

    def create(self, goal: Goal) -> Goal:
        if goal.id in self._goals:
            raise ValueError(f"Goal {goal.id} already exists")
        self._goals[goal.id] = goal
        return goal

    def get(self, goal_id: str) -> Goal:
        return self._goals[goal_id]

    def active(self) -> list[Goal]:
        candidates = [goal for goal in self._goals.values() if goal.status == "active" and self._dependencies_met(goal)]
        return sorted(candidates, key=lambda goal: goal.priority, reverse=True)

    def update_progress(self, goal_id: str, progress: float) -> Goal:
        goal = self.get(goal_id)
        goal.progress = max(0.0, min(1.0, progress))
        if goal.progress >= 1.0:
            goal.status = "completed"
        return goal

    def _dependencies_met(self, goal: Goal) -> bool:
        return all(self._goals.get(goal_id) and self._goals[goal_id].status == "completed" for goal_id in goal.dependencies)
