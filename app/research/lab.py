"""Research lab orchestration boundary."""

from __future__ import annotations

from typing import Any

from app.ai.context import AIContext
from app.ai.events import (EventBus, ExperimentCompletedEvent, ExperimentQueuedEvent,
                           ExperimentStartedEvent, HypothesisCreatedEvent,
                           LeaderboardUpdatedEvent, NewFeatureDiscoveredEvent,
                           NewStrategyGeneratedEvent, ResearchPublishedEvent)
from app.ai.knowledge_base import KnowledgeBase, KnowledgeItem
from app.ai.memory import AIMemory
from app.research.experiment_scheduler import ExperimentScheduler
from app.research.feature_discovery import FeatureDiscovery
from app.research.hypothesis import Hypothesis
from app.research.ranking import RankingEngine
from app.research.result_analyzer import ResultAnalyzer
from app.research.strategy_generator import StrategyGenerator


class ResearchLab:
    """Coordinates research queues, artifacts, published outcomes, and feedback."""

    def __init__(self, *, context: AIContext, memory: AIMemory, knowledge_base: KnowledgeBase, event_bus: EventBus, scheduler: ExperimentScheduler | None = None, feature_discovery: FeatureDiscovery | None = None, strategy_generator: StrategyGenerator | None = None, analyzer: ResultAnalyzer | None = None, ranking: RankingEngine | None = None) -> None:
        self.context, self.memory, self.knowledge_base, self.event_bus = context, memory, knowledge_base, event_bus
        self.scheduler = scheduler or ExperimentScheduler()
        self.feature_discovery = feature_discovery or FeatureDiscovery()
        self.strategy_generator = strategy_generator or StrategyGenerator()
        self.analyzer, self.ranking = analyzer or ResultAnalyzer(), ranking or RankingEngine()
        self.hypotheses: dict[str, Hypothesis] = {}
        self.active_experiments: dict[str, dict[str, Any]] = {}
        self.published_research: list[dict[str, Any]] = []

    def register_hypothesis(self, hypothesis: Hypothesis) -> Hypothesis:
        self.hypotheses[hypothesis.id] = hypothesis
        self.memory.add("research_hypothesis", {"id": hypothesis.id, "description": hypothesis.description})
        self.event_bus.publish(HypothesisCreatedEvent(hypothesis.id, {"description": hypothesis.description}))
        return hypothesis

    def prepare_candidates(self) -> tuple[list[Any], list[Any]]:
        features, strategies = self.feature_discovery.discover(), self.strategy_generator.generate()
        for feature in features:
            self.event_bus.publish(NewFeatureDiscoveredEvent(feature.name))
        for strategy in strategies:
            self.event_bus.publish(NewStrategyGeneratedEvent(strategy.name))
        return features, strategies

    def queue_experiment(self, experiment_id: str, *, hypothesis: Hypothesis, priority: int | None = None, cost: float = 1.0, expected_value: float = 0.0, payload: dict[str, Any] | None = None) -> bool:
        queued = self.scheduler.queue(experiment_id, priority=priority if priority is not None else hypothesis.priority, cost=cost, expected_value=expected_value, payload={"hypothesis_id": hypothesis.id, **(payload or {})})
        if queued:
            self.event_bus.publish(ExperimentQueuedEvent(experiment_id))
        return queued

    def start_next(self) -> dict[str, Any] | None:
        batch = self.scheduler.next_batch(1)
        if not batch:
            return None
        experiment = batch[0]
        self.active_experiments[experiment["id"]] = experiment
        self.event_bus.publish(ExperimentStartedEvent(experiment["id"]))
        return experiment

    def complete(self, experiment_id: str, metrics: dict[str, float], *, baseline: dict[str, float] | None = None) -> dict[str, Any]:
        experiment = self.active_experiments.pop(experiment_id, {"id": experiment_id, "payload": {}})
        analysis = self.analyzer.analyze(metrics, baseline=baseline)
        ranking = self.ranking.update(experiment_id, analysis)
        outcome = {"experiment_id": experiment_id, **analysis, "ranking": ranking, "completed": True}
        self.memory.add("research_result", outcome)
        self.knowledge_base.add_item(KnowledgeItem(kind="research_result", title=experiment_id, summary=f"Research score: {analysis['score']:.4f}", tags=["research", "success" if analysis["score"] > 0 else "failure"], source="research_lab", confidence=min(1.0, max(0.0, analysis["score"] / 3))))
        if analysis["score"] <= 0:
            self.memory.add("research_failure", {"signature": experiment["payload"].get("signature", experiment_id)})
        self.event_bus.publish(ExperimentCompletedEvent(experiment_id, outcome))
        self.event_bus.publish(LeaderboardUpdatedEvent(experiment_id, {"score": ranking["score"]}))
        return outcome

    def publish(self, result: dict[str, Any]) -> dict[str, Any]:
        self.published_research.append(result)
        self.event_bus.publish(ResearchPublishedEvent(result["experiment_id"], result))
        return result
