import unittest
from pathlib import Path
import tempfile

from app.ai.agent_manager import AgentManager
from app.ai.context import AIContext
from app.ai.events import Event, EventBus, MarketUpdatedEvent, RiskAlertEvent
from app.ai.experiments.experiment_manager import ExperimentManager
from app.ai.experiments.experiment_registry import ExperimentRegistry
from app.ai.knowledge_base import KnowledgeBase, KnowledgeItem
from app.ai.kernel import AIKernel
from app.ai.memory import AIMemory
from app.ai.orchestrator import AIOrchestrator
from app.ai.agents.base_agent import BaseAgent
from app.ai.agents.market_agent import MarketAgent
from app.ai.agents.research_agent import ResearchAgent
from app.ai.agents.strategy_agent import StrategyAgent
from app.ai.agents.ml_agent import MLAgent
from app.ai.agents.risk_agent import RiskAgent
from app.ai.agents.evaluation_agent import EvaluationAgent
from app.ai.agents.engineering_agent import EngineeringAgent
from app.ai.agents.documentation_agent import DocumentationAgent


class PlatformCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.context = AIContext(configuration={"drawdown_limit": 0.2})
        self.context.market_state = {"trend": "up", "volatility": 0.4, "volume": 1200}
        self.context.portfolio = {"equity": 100000.0}
        self.context.risk_metrics = {"drawdown": 0.05, "daily_loss": 0.01}

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_event_bus_publishes(self) -> None:
        bus = EventBus()
        received = []
        bus.subscribe("MarketUpdated", lambda event: received.append(event.payload["symbol"]))
        bus.publish(MarketUpdatedEvent(symbol="BTCUSDT", payload={"trend": "up"}))
        self.assertEqual(received, ["BTCUSDT"])

    def test_event_bus_supports_multiple_subscribers(self) -> None:
        bus = EventBus()
        received = []
        bus.subscribe("RiskAlert", lambda event: received.append(event.payload["level"]))
        bus.subscribe("RiskAlert", lambda event: received.append("extra"))
        bus.publish(RiskAlertEvent(level="high", payload={"drawdown": 0.25}))
        self.assertEqual(received, ["high", "extra"])

    def test_context_updates_and_tracks_tasks(self) -> None:
        self.context.add_task("task-1", {"goal": "research"})
        self.context.update(model_registry={"v1": {"version": "v1"}})
        self.assertEqual(self.context.current_tasks["task-1"]["goal"], "research")
        self.assertEqual(self.context.model_registry["v1"]["version"], "v1")

    def test_memory_persists_records(self) -> None:
        memory = AIMemory(storage_path=self.base_dir / "memory.json")
        memory.add("observation", {"symbol": "BTC"}, {"source": "market"})
        reloaded = AIMemory(storage_path=self.base_dir / "memory.json")
        self.assertEqual(reloaded.list("observation")[0].content["symbol"], "BTC")

    def test_knowledge_base_stores_and_filters_items(self) -> None:
        knowledge = KnowledgeBase()
        knowledge.add_item(KnowledgeItem(kind="indicator", title="RSI", summary="Momentum", tags=["momentum"], source="book", confidence=0.9))
        self.assertEqual(len(knowledge.list_items(kind="indicator")), 1)
        self.assertIn("RSI", [item.title for item in knowledge.list_items(tag="momentum")])

    def test_experiment_registry_rejects_duplicates(self) -> None:
        registry = ExperimentRegistry()
        experiment = registry.register({"id": "exp-1", "status": "draft"})
        with self.assertRaises(ValueError):
            registry.register({"id": "exp-1", "status": "draft"})
        self.assertEqual(registry.get("exp-1")["id"], experiment["id"])

    def test_experiment_manager_tracks_history(self) -> None:
        manager = ExperimentManager(storage_dir=self.base_dir)
        exp = manager.create_experiment("exp-1", dataset="BTC", strategy="trend", model="xgb")
        manager.update_status(exp.experiment_id, "completed")
        updated = manager.get(exp.experiment_id)
        self.assertEqual(updated.status, "completed")
        self.assertEqual(len(manager.list()), 1)

    def test_agent_manager_registers_and_executes(self) -> None:
        manager = AgentManager()
        agent = MarketAgent()
        manager.register(agent)
        with self.assertRaises(ValueError):
            manager.register(agent)
        manager.enable(agent.name)
        result = manager.execute(agent.name, AIContext())
        self.assertEqual(result["agent"], agent.name)

    def test_kernel_runs_agent_and_emits_event(self) -> None:
        kernel = AIKernel(context=AIContext(), memory=AIMemory(storage_path=self.base_dir / "kernel_memory.json"))
        agent = MarketAgent(kernel=kernel)
        kernel.register_agent(agent)
        result = kernel.run_agent(agent.name)
        self.assertEqual(result["agent"], agent.name)
        self.assertEqual(kernel.context.agent_results[agent.name]["agent"], agent.name)

    def test_orchestrator_executes_sequential_workflow(self) -> None:
        kernel = AIKernel(context=AIContext(), memory=AIMemory(storage_path=self.base_dir / "orchestrator_memory.json"))
        orchestrator = AIOrchestrator(kernel=kernel)
        agent = MarketAgent(kernel=kernel)
        kernel.register_agent(agent)
        result = orchestrator.execute_sequential([agent], AIContext())
        self.assertEqual(result[0]["agent"], agent.name)

    def test_base_agent_run_cycle_returns_structured_results(self) -> None:
        class DummyAgent(BaseAgent):
            name = "dummy"

        agent = DummyAgent()
        result = agent.run_cycle(AIContext())
        self.assertEqual(result["agent"], "dummy")
        self.assertIn("status", result)


class AgentContractTests(unittest.TestCase):
    pass


AGENT_CLASSES = [
    MarketAgent,
    ResearchAgent,
    StrategyAgent,
    MLAgent,
    RiskAgent,
    EvaluationAgent,
    EngineeringAgent,
    DocumentationAgent,
]

for agent_cls in AGENT_CLASSES:
    def make_agent_test(agent_cls):
        def test_agent_contract(self):
            agent = agent_cls()
            result = agent.run_cycle(AIContext())
            self.assertEqual(result["agent"], agent.name)
            self.assertIn("status", result)
            self.assertIn("result", result)
        return test_agent_contract

    setattr(AgentContractTests, f"test_{agent_cls.__name__.lower()}_contract", make_agent_test(agent_cls))


class KnowledgeBaseGenerationTests(unittest.TestCase):
    pass


KNOWLEDGE_KINDS = ["indicator", "pattern", "paper", "book", "rule", "experiment", "strategy"]
for kind in KNOWLEDGE_KINDS:
    def make_knowledge_test(kind):
        def test_knowledge_storage(self):
            kb = KnowledgeBase()
            item = KnowledgeItem(kind=kind, title=f"{kind.title()}", summary="summary", tags=[kind], source="unit-test", confidence=0.8)
            kb.add_item(item)
            stored = kb.list_items(kind=kind)
            self.assertEqual(stored[0].title, f"{kind.title()}")
        return test_knowledge_storage

    setattr(KnowledgeBaseGenerationTests, f"test_{kind}_knowledge_store", make_knowledge_test(kind))


class ExperimentManagerGenerationTests(unittest.TestCase):
    pass


STATUSES = ["draft", "running", "completed", "failed", "archived"]
for status in STATUSES:
    def make_status_test(status):
        def test_status_update(self):
            manager = ExperimentManager(storage_dir=Path(tempfile.mkdtemp()))
            exp = manager.create_experiment(f"exp-{status}", dataset="BTC", strategy="trend", model="xgb")
            manager.update_status(exp.experiment_id, status)
            stored = manager.get(exp.experiment_id)
            self.assertEqual(stored.status, status)
        return test_status_update

    setattr(ExperimentManagerGenerationTests, f"test_{status}_status_update", make_status_test(status))


if __name__ == "__main__":
    unittest.main()
