import tempfile
import unittest
from pathlib import Path

from app.ai.context import AIContext
from app.ai.events import EventBus
from app.ai.memory import AIMemory
from app.cognition.attention import AttentionItem, AttentionSystem
from app.cognition.brain import AIBrain
from app.cognition.critic import Critic
from app.cognition.decision_engine import DecisionEngine
from app.cognition.goal_manager import Goal, GoalManager
from app.cognition.planner import Planner
from app.cognition.reasoner import Reasoner
from app.cognition.reflection import ReflectionEngine
from app.cognition.task_manager import TaskManager


class CognitionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory = AIMemory(Path(self.temp_dir.name) / "memory.json")
        self.context = AIContext(market_state={"regime": "trending"})
        self.events = EventBus()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_goal_manager_prioritizes_unblocked_goals(self):
        manager = GoalManager()
        completed = manager.create(Goal("Foundation", priority=1, status="completed"))
        manager.create(Goal("Improve Sharpe", priority=9, dependencies=[completed.id]))
        self.assertEqual(manager.active()[0].title, "Improve Sharpe")

    def test_planner_creates_dependency_graph(self):
        manager = TaskManager()
        tasks = Planner(manager).plan(Goal("Improve Sharpe"))
        self.assertEqual(len(tasks), 4)
        self.assertEqual(tasks[1].dependencies, [tasks[0].id])

    def test_reasoner_selects_explained_best_action(self):
        choice = Reasoner().select([{"name": "safe", "expected_return": .4, "confidence": .9, "risk": .1, "historical_performance": .7}, {"name": "risky", "expected_return": .8, "confidence": .4, "risk": .9}])
        self.assertEqual(choice.name, "safe")
        self.assertTrue(choice.explanation)

    def test_decision_engine_ranks_actions(self):
        ranked = DecisionEngine().decide([{"name": "a", "expected_return": .4, "confidence": .8, "risk": .1}, {"name": "b", "expected_return": .1, "confidence": .2, "risk": .7}], market_regime="volatile")
        self.assertEqual(ranked[0].name, "a")

    def test_attention_prioritizes_risk_alert(self):
        ranked = AttentionSystem().prioritize([AttentionItem("completed_report", 5, {}), AttentionItem("risk_alert", 0, {})])
        self.assertEqual(ranked[0].topic, "risk_alert")

    def test_reflection_persists_lesson(self):
        reflection = ReflectionEngine(self.memory).reflect({"experiment_id": "exp", "score": -1})
        self.assertTrue(reflection.failed)
        self.assertEqual(len(self.memory.list("reflection")), 1)

    def test_critic_rejects_poor_idea(self):
        critique = Critic().review({"score": -1, "risk": .8, "risk_limit": .2, "confidence": .1})
        self.assertFalse(critique.accepted)
        self.assertGreaterEqual(len(critique.reasons), 2)

    def test_brain_plans_decides_and_reflects(self):
        brain = AIBrain(context=self.context, memory=self.memory, event_bus=self.events)
        goal, tasks = brain.create_goal(Goal("Reduce Drawdown", priority=8))
        self.assertEqual(brain.next_task().id, tasks[0].id)
        decision = brain.decide([{"name": "tighten stops", "expected_return": .3, "confidence": .8, "risk": .1}])
        self.assertEqual(decision.name, "tighten stops")
        self.assertTrue(brain.reflect_on_experiment({"experiment_id": "x", "score": 1}).worked)
        self.assertEqual(goal.status, "active")


if __name__ == "__main__":
    unittest.main()
