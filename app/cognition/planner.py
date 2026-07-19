"""Goal decomposition into an explicit task graph."""

from __future__ import annotations

from app.cognition.goal_manager import Goal
from app.cognition.task_manager import Task, TaskManager


class Planner:
    """Turns a goal into a research-to-deployment dependency chain."""

    STAGES = ("Research", "Experiments", "Evaluation", "Deployment Candidate")

    def __init__(self, task_manager: TaskManager) -> None:
        self.task_manager = task_manager

    def plan(self, goal: Goal) -> list[Task]:
        previous_id: str | None = None
        tasks: list[Task] = []
        for offset, stage in enumerate(self.STAGES):
            task = self.task_manager.create(Task(title=f"{stage}: {goal.title}", goal_id=goal.id, priority=max(1, goal.priority - offset), dependencies=[previous_id] if previous_id else []))
            tasks.append(task)
            previous_id = task.id
        return tasks
