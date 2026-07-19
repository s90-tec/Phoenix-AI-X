"""Top-level cognitive coordinator."""

from __future__ import annotations

from typing import Any

from app.ai.context import AIContext
from app.ai.events import (CritiqueGeneratedEvent, DecisionMadeEvent, EventBus,
                           GoalCompletedEvent, GoalCreatedEvent,
                           ReflectionCompletedEvent, TaskCreatedEvent, TaskFailedEvent)
from app.ai.memory import AIMemory
from app.cognition.critic import Critic, Critique
from app.cognition.decision_engine import DecisionEngine
from app.cognition.goal_manager import Goal, GoalManager
from app.cognition.planner import Planner
from app.cognition.reflection import Reflection, ReflectionEngine
from app.cognition.scheduler import CognitiveScheduler
from app.cognition.task_manager import Task, TaskManager
from app.cognition.working_memory import WorkingMemory
from app.cognition.reasoner import ReasonedAction


class AIBrain:
    """Coordinates goal-driven, explainable planning and self-improvement."""

    def __init__(self, *, context: AIContext, memory: AIMemory, event_bus: EventBus, goal_manager: GoalManager | None = None, task_manager: TaskManager | None = None, decision_engine: DecisionEngine | None = None, critic: Critic | None = None, working_memory: WorkingMemory | None = None) -> None:
        self.context, self.memory, self.event_bus = context, memory, event_bus
        self.goal_manager = goal_manager or GoalManager()
        self.task_manager = task_manager or TaskManager()
        self.planner = Planner(self.task_manager)
        self.scheduler = CognitiveScheduler(self.task_manager)
        self.decision_engine = decision_engine or DecisionEngine()
        self.critic = critic or Critic()
        self.working_memory = working_memory or WorkingMemory()
        self.reflection = ReflectionEngine(memory)

    def create_goal(self, goal: Goal) -> tuple[Goal, list[Task]]:
        created = self.goal_manager.create(goal)
        self.event_bus.publish(GoalCreatedEvent(created.id, {"title": created.title}))
        tasks = self.planner.plan(created)
        for task in tasks:
            self.event_bus.publish(TaskCreatedEvent(task.id, {"goal_id": created.id, "title": task.title}))
        self._refresh_memory()
        return created, tasks

    def next_task(self) -> Task | None:
        return self.scheduler.next_task()

    def complete_task(self, task_id: str) -> Task:
        task = self.task_manager.transition(task_id, "completed")
        tasks = self.task_manager.by_goal(task.goal_id)
        if tasks and all(item.status == "completed" for item in tasks):
            goal = self.goal_manager.update_progress(task.goal_id, 1.0)
            self.event_bus.publish(GoalCompletedEvent(goal.id, {"title": goal.title}))
        self._refresh_memory()
        return task

    def fail_task(self, task_id: str, reason: str) -> Task:
        task = self.task_manager.transition(task_id, "failed")
        self.event_bus.publish(TaskFailedEvent(task.id, {"reason": reason}))
        self._refresh_memory()
        return task

    def decide(self, actions: list[dict[str, Any]]) -> ReasonedAction:
        ranked = self.decision_engine.decide(actions, market_regime=str(self.context.market_state.get("regime", "unknown")))
        if not ranked:
            raise ValueError("No actions available for decision")
        decision = ranked[0]
        self.memory.add("decision", {"name": decision.name, "score": decision.score, "explanation": decision.explanation})
        self.event_bus.publish(DecisionMadeEvent(decision.name, {"score": decision.score, "explanation": decision.explanation}))
        return decision

    def reflect_on_experiment(self, result: dict[str, Any]) -> Reflection:
        reflection = self.reflection.reflect(result)
        self.event_bus.publish(ReflectionCompletedEvent(str(result.get("experiment_id", "unknown")), {"lessons": reflection.lessons}))
        return reflection

    def critique(self, proposal: dict[str, Any]) -> Critique:
        critique = self.critic.review(proposal)
        self.event_bus.publish(CritiqueGeneratedEvent(str(proposal.get("name", "proposal")), {"accepted": critique.accepted, "reasons": critique.reasons}))
        return critique

    def _refresh_memory(self) -> None:
        self.working_memory.set("current_goals", self.goal_manager.active())
        self.working_memory.set("market_state", self.context.market_state)
        self.working_memory.set("open_tasks", self.task_manager.ready())
        self.working_memory.set("pending_risks", self.context.risk_metrics)
