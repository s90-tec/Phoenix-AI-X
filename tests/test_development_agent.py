import unittest
from pathlib import Path
import tempfile

from app.development.development_agent import DevelopmentAgent
from app.development.evaluation_pipeline import EvaluationPipeline
from app.development.experiment_manager import ExperimentManager
from app.development.model_registry import ModelRegistry, ModelRecord
from app.development.performance_monitor import PerformanceMonitor
from app.development.auto_retraining_scheduler import AutoRetrainingScheduler


class DevelopmentAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_registry_archives_previous_production_model(self) -> None:
        registry = ModelRegistry(storage_dir=self.base_dir)
        production = registry.register_model(
            version="v1",
            artifact_path="/tmp/v1.pkl",
            training_data_range=("2024-01-01", "2024-06-30"),
            hyperparameters={"lr": 0.01},
            validation_metrics={"accuracy": 0.8, "sharpe": 1.2},
            backtest_metrics={"profit": 100.0, "max_drawdown": 0.08},
            deployment_status="production",
        )
        candidate = registry.register_model(
            version="v2",
            artifact_path="/tmp/v2.pkl",
            training_data_range=("2024-02-01", "2024-07-31"),
            hyperparameters={"lr": 0.005},
            validation_metrics={"accuracy": 0.82, "sharpe": 1.4},
            backtest_metrics={"profit": 140.0, "max_drawdown": 0.07},
            deployment_status="candidate",
        )

        registry.promote_model(candidate.version)

        production_record = registry.get_model("v1")
        self.assertEqual(production_record.deployment_status, "archived")
        promoted = registry.get_model("v2")
        self.assertEqual(promoted.deployment_status, "production")

    def test_performance_monitor_detects_degradation(self) -> None:
        monitor = PerformanceMonitor(degradation_threshold=0.1, drawdown_limit=0.2)
        current = {"sharpe": 1.0, "accuracy": 0.7, "max_drawdown": 0.25}
        baseline = {"sharpe": 1.3, "accuracy": 0.8, "max_drawdown": 0.1}
        result = monitor.analyze(current, baseline)
        self.assertTrue(result["degraded"])
        self.assertIn("max_drawdown", result["issues"])

    def test_evaluation_pipeline_runs_test_stages(self) -> None:
        pipeline = EvaluationPipeline(
            unit_test_runner=lambda: {"passed": True, "details": "unit"},
            integration_test_runner=lambda: {"passed": True, "details": "integration"},
            backtest_runner=lambda model: {"passed": True, "metrics": {"profit": 200.0, "max_drawdown": 0.09}},
        )

        result = pipeline.evaluate(ModelRecord(version="v3", artifact_path="/tmp/v3.pkl", training_data_range=("2024-03-01", "2024-08-31"), hyperparameters={}, validation_metrics={}, backtest_metrics={}))
        self.assertTrue(result["unit_tests"]["passed"])
        self.assertTrue(result["integration_tests"]["passed"])
        self.assertTrue(result["backtest"]["passed"])

    def test_experiment_manager_creates_branch_and_report(self) -> None:
        manager = ExperimentManager(storage_dir=self.base_dir)
        experiment = manager.create_experiment("v4", "v3", {"lr": 0.001})
        self.assertEqual(experiment.branch_name, "exp/v4")
        self.assertTrue(Path(experiment.report_path).exists())

    def test_development_agent_promotes_only_when_safe(self) -> None:
        registry = ModelRegistry(storage_dir=self.base_dir)
        production = registry.register_model(
            version="prod",
            artifact_path="/tmp/prod.pkl",
            training_data_range=("2024-01-01", "2024-06-30"),
            hyperparameters={"lr": 0.01},
            validation_metrics={"accuracy": 0.8, "sharpe": 1.2},
            backtest_metrics={"profit": 100.0, "max_drawdown": 0.08},
            deployment_status="production",
        )
        candidate = registry.register_model(
            version="cand",
            artifact_path="/tmp/cand.pkl",
            training_data_range=("2024-02-01", "2024-07-31"),
            hyperparameters={"lr": 0.005},
            validation_metrics={"accuracy": 0.82, "sharpe": 1.4},
            backtest_metrics={"profit": 140.0, "max_drawdown": 0.07},
            deployment_status="candidate",
        )

        monitor = PerformanceMonitor(degradation_threshold=0.1, drawdown_limit=0.2)
        pipeline = EvaluationPipeline(
            unit_test_runner=lambda: {"passed": True, "details": "unit"},
            integration_test_runner=lambda: {"passed": True, "details": "integration"},
            backtest_runner=lambda model: {"passed": True, "metrics": {"profit": 140.0, "max_drawdown": 0.07}},
        )
        manager = ExperimentManager(storage_dir=self.base_dir)
        scheduler = AutoRetrainingScheduler(interval_minutes=60)
        agent = DevelopmentAgent(
            registry=registry,
            performance_monitor=monitor,
            evaluation_pipeline=pipeline,
            experiment_manager=manager,
            retraining_scheduler=scheduler,
            drawdown_limit=0.2,
        )

        decision = agent.run_cycle(candidate, production, baseline_metrics={"sharpe": 1.2, "accuracy": 0.8, "max_drawdown": 0.08})
        self.assertTrue(decision["promoted"])
        self.assertEqual(registry.get_model("cand").deployment_status, "production")


if __name__ == "__main__":
    unittest.main()
