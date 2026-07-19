from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class Event:
    """Base event object used by the agent event bus."""

    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketUpdatedEvent(Event):
    def __init__(self, symbol: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="MarketUpdated", payload={"symbol": symbol, **(payload or {})})


@dataclass
class NewTradeEvent(Event):
    def __init__(self, symbol: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="NewTrade", payload={"symbol": symbol, **(payload or {})})


@dataclass
class ModelFinishedTrainingEvent(Event):
    def __init__(self, model_name: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="ModelFinishedTraining", payload={"model_name": model_name, **(payload or {})})


@dataclass
class StrategyCreatedEvent(Event):
    def __init__(self, strategy_name: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="StrategyCreated", payload={"strategy_name": strategy_name, **(payload or {})})


@dataclass
class BacktestCompletedEvent(Event):
    def __init__(self, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="BacktestCompleted", payload=payload or {})


@dataclass
class RiskAlertEvent(Event):
    def __init__(self, level: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="RiskAlert", payload={"level": level, **(payload or {})})


@dataclass
class ExperimentCompletedEvent(Event):
    def __init__(self, experiment_id: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="ExperimentCompleted", payload={"experiment_id": experiment_id, **(payload or {})})


@dataclass
class HypothesisCreatedEvent(Event):
    def __init__(self, hypothesis_id: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="HypothesisCreated", payload={"hypothesis_id": hypothesis_id, **(payload or {})})


@dataclass
class ExperimentQueuedEvent(Event):
    def __init__(self, experiment_id: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="ExperimentQueued", payload={"experiment_id": experiment_id, **(payload or {})})


@dataclass
class ExperimentStartedEvent(Event):
    def __init__(self, experiment_id: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="ExperimentStarted", payload={"experiment_id": experiment_id, **(payload or {})})


@dataclass
class ResearchPublishedEvent(Event):
    def __init__(self, research_id: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="ResearchPublished", payload={"research_id": research_id, **(payload or {})})


@dataclass
class NewFeatureDiscoveredEvent(Event):
    def __init__(self, feature_name: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="NewFeatureDiscovered", payload={"feature_name": feature_name, **(payload or {})})


@dataclass
class NewStrategyGeneratedEvent(Event):
    def __init__(self, strategy_name: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="NewStrategyGenerated", payload={"strategy_name": strategy_name, **(payload or {})})


@dataclass
class LeaderboardUpdatedEvent(Event):
    def __init__(self, item_id: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="LeaderboardUpdated", payload={"item_id": item_id, **(payload or {})})


@dataclass
class GoalCreatedEvent(Event):
    def __init__(self, goal_id: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="GoalCreated", payload={"goal_id": goal_id, **(payload or {})})


@dataclass
class GoalCompletedEvent(Event):
    def __init__(self, goal_id: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="GoalCompleted", payload={"goal_id": goal_id, **(payload or {})})


@dataclass
class TaskCreatedEvent(Event):
    def __init__(self, task_id: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="TaskCreated", payload={"task_id": task_id, **(payload or {})})


@dataclass
class TaskFailedEvent(Event):
    def __init__(self, task_id: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="TaskFailed", payload={"task_id": task_id, **(payload or {})})


@dataclass
class DecisionMadeEvent(Event):
    def __init__(self, decision_name: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="DecisionMade", payload={"decision_name": decision_name, **(payload or {})})


@dataclass
class ReflectionCompletedEvent(Event):
    def __init__(self, result_id: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="ReflectionCompleted", payload={"result_id": result_id, **(payload or {})})


@dataclass
class CritiqueGeneratedEvent(Event):
    def __init__(self, subject: str, payload: Dict[str, Any] | None = None) -> None:
        super().__init__(event_type="CritiqueGenerated", payload={"subject": subject, **(payload or {})})


class EventBus:
    """Simple in-process event bus for decoupled agent communication."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        self._subscribers.setdefault(event_type, []).append(callback)

    def publish(self, event: Event) -> None:
        for callback in self._subscribers.get(event.event_type, []):
            callback(event)
