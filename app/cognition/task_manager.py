"""Task lifecycle and dependency management."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any


TASK_STATUSES = {"queued", "running", "completed", "failed", "blocked", "cancelled"}


@dataclass
class Task:
    title: str
    goal_id: str
    priority: int = 1
    dependencies: list[str] = field(default_factory=list)
    status: str = "queued"
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if self.status not in TASK_STATUSES:
            raise ValueError(f"Unknown task status: {self.status}")


class TaskManager:
    """Tracks task states and releases only dependency-ready work."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def create(self, task: Task) -> Task:
        if task.id in self._tasks:
            raise ValueError(f"Task {task.id} already exists")
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Task:
        return self._tasks[task_id]

    def transition(self, task_id: str, status: str) -> Task:
        if status not in TASK_STATUSES:
            raise ValueError(f"Unknown task status: {status}")
        task = self.get(task_id)
        if status == "running" and not self.dependencies_met(task):
            raise ValueError("Cannot start a task with incomplete dependencies")
        task.status = status
        return task

    def ready(self, goal_id: str | None = None) -> list[Task]:
        tasks = [task for task in self._tasks.values() if task.status == "queued" and self.dependencies_met(task)]
        if goal_id is not None:
            tasks = [task for task in tasks if task.goal_id == goal_id]
        return sorted(tasks, key=lambda task: task.priority, reverse=True)

    def by_goal(self, goal_id: str) -> list[Task]:
        return [task for task in self._tasks.values() if task.goal_id == goal_id]

    def dependencies_met(self, task: Task) -> bool:
        return all(self._tasks.get(task_id) and self._tasks[task_id].status == "completed" for task_id in task.dependencies)
