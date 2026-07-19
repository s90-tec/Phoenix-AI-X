"""Cognitive work scheduler."""

from __future__ import annotations

from app.cognition.task_manager import Task, TaskManager


class CognitiveScheduler:
    """Selects the next highest-priority dependency-ready task."""

    def __init__(self, task_manager: TaskManager) -> None:
        self.task_manager = task_manager

    def next_task(self) -> Task | None:
        ready = self.task_manager.ready()
        return ready[0] if ready else None
