import tempfile
import unittest
from pathlib import Path

from app.ai.context import AIContext
from app.ai.events import EventBus
from app.ai.knowledge_base import KnowledgeBase, KnowledgeItem
from app.ai.memory import AIMemory
from app.research.experiment_scheduler import ExperimentScheduler
from app.research.feature_discovery import FeatureDiscovery
from app.research.hypothesis import Hypothesis
from app.research.idea_generator import IdeaGenerator
from app.research.lab import ResearchLab
from app.research.parameter_optimizer import ParameterOptimizer
from app.research.pipeline import ResearchPipeline
from app.research.ranking import RankingEngine
from app.research.result_analyzer import ResultAnalyzer
from app.research.strategy_generator import StrategyGenerator


class ResearchLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.context = AIContext(configuration={"drawdown_limit": 0.2})
        self.context.market_state = {"trend": "up", "volatility": 0.4, "volume": 1200}
        self.context.portfolio = {"equity": 100000.0}
        self.context.risk_metrics = {"drawdown": 0.05, "daily_loss": 0.01}
        self.memory = AIMemory(storage_path=self.base_dir / "research_memory.json")
        self.knowledge = KnowledgeBase()
        self.knowledge.add_item(KnowledgeItem(kind="indicator", title="RSI", summary="Momentum", tags=["momentum"], source="book", confidence=0.9))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_hypothesis_structure(self) -> None:
        hypothesis = Hypothesis(description="Higher RSI with ADX", reasoning="Trend confirmation", expected_outcome="better entries", priority=2, status="draft", confidence=0.8)
        self.assertEqual(hypothesis.status, "draft")
        self.assertEqual(hypothesis.priority, 2)

    def test_idea_generator_produces_non_duplicate_ideas(self) -> None:
        generator = IdeaGenerator(knowledge_base=self.knowledge, memory=self.memory)
        ideas = generator.generate_many(limit=3, previous_failures=["RSI+ADX"], previous_successes=["EMA+RSI"])
        self.assertTrue(len(ideas) >= 1)
        self.assertTrue(all(idea.description for idea in ideas))

    def test_feature_discovery_generates_features(self) -> None:
        discovery = FeatureDiscovery()
        features = discovery.discover()
        self.assertTrue(any(feature.name == "EMA_spread" for feature in features))
        self.assertTrue(any(feature.name == "ATR_expansion" for feature in features))

    def test_strategy_generator_registers_candidates(self) -> None:
        generator = StrategyGenerator()
        strategies = generator.generate()
        self.assertTrue(strategies)
        self.assertTrue(any(strategy.name == "trend_volatility_breakout" for strategy in strategies))

    def test_optimizer_supports_search_modes(self) -> None:
        optimizer = ParameterOptimizer()
        result = optimizer.optimize({"threshold": [0.1, 0.2]}, mode="grid")
        self.assertIn("threshold", result["best_params"])
        self.assertEqual(result["mode"], "grid")

    def test_scheduler_prioritizes_and_deduplicates(self) -> None:
        scheduler = ExperimentScheduler()
        scheduler.queue("exp-1", priority=3, cost=1.0)
        scheduler.queue("exp-2", priority=1, cost=5.0)
        scheduler.queue("exp-1", priority=3, cost=1.0)
        queued = scheduler.next_batch(2)
        self.assertEqual([item["id"] for item in queued], ["exp-1", "exp-2"])

    def test_result_analyzer_computes_metrics(self) -> None:
        analyzer = ResultAnalyzer()
        result = analyzer.analyze({"sharpe": 1.8, "sortino": 1.4, "win_rate": 0.62, "drawdown": 0.1, "profit_factor": 1.7, "recovery_factor": 2.2, "expectancy": 0.4}, baseline={"sharpe": 1.2})
        self.assertGreater(result["score"], 0)
        self.assertEqual(result["comparison"]["sharpe"], 0.6)

    def test_ranking_engine_tracks_history(self) -> None:
        ranking = RankingEngine()
        ranking.update("idea-1", {"score": 0.8})
        ranking.update("idea-2", {"score": 0.6})
        ranked = ranking.leaderboard(limit=5)
        self.assertEqual(ranked[0]["item_id"], "idea-1")
        self.assertEqual(len(ranking.history("idea-1")), 1)

    def test_research_lab_executes_pipeline(self) -> None:
        lab = ResearchLab(context=self.context, memory=self.memory, knowledge_base=self.knowledge, event_bus=EventBus())
        pipeline = ResearchPipeline(lab=lab)
        result = pipeline.run(hypothesis=Hypothesis(description="RSI + ADX", reasoning="trend", expected_outcome="improvement", priority=1, status="draft", confidence=0.7))
        self.assertTrue(result["completed"])
        self.assertIn("hypothesis_id", result)


if __name__ == "__main__":
    unittest.main()
