from __future__ import annotations

from typing import Any

from app.development.auto_retraining_scheduler import AutoRetrainingScheduler
from app.development.evaluation_pipeline import EvaluationPipeline
from app.development.experiment_manager import ExperimentManager
from app.development.model_registry import ModelRecord, ModelRegistry
from app.development.performance_monitor import PerformanceMonitor


class DevelopmentAgent:
    """Coordinate autonomous model improvement while preserving production safety."""

    def __init__(
        self,
        *,
        registry: ModelRegistry,
        performance_monitor: PerformanceMonitor,
        evaluation_pipeline: EvaluationPipeline,
        experiment_manager: ExperimentManager,
        retraining_scheduler: AutoRetrainingScheduler,
        drawdown_limit: float = 0.2,
    ) -> None:
        self.registry = registry
        self.performance_monitor = performance_monitor
        self.evaluation_pipeline = evaluation_pipeline
        self.experiment_manager = experiment_manager
        self.retraining_scheduler = retraining_scheduler
        self.drawdown_limit = drawdown_limit

    def run_cycle(self, candidate: ModelRecord, production: ModelRecord, *, baseline_metrics: dict[str, float]) -> dict[str, Any]:
        if not self.retraining_scheduler.should_run():
            return {"promoted": False, "reason": "retraining not due"}

        experiment = self.experiment_manager.create_experiment(candidate.version, production.version, candidate.hyperparameters)
        evaluation = self.evaluation_pipeline.evaluate(candidate)
        performance = self.performance_monitor.analyze(
            current_metrics={
                **candidate.validation_metrics,
                **candidate.backtest_metrics,
            },
            baseline_metrics=baseline_metrics,
        )
        candidate.experiment_branch = experiment.branch_name
        candidate.report_path = experiment.report_path
        self.registry._persist(candidate)

        report_payload = {
            "version": candidate.version,
            "branch_name": experiment.branch_name,
            "baseline_version": experiment.baseline_version,
            "hyperparameters": candidate.hyperparameters,
            "validation_metrics": candidate.validation_metrics,
            "backtest_metrics": candidate.backtest_metrics,
            "performance_monitor": performance,
            "evaluation": evaluation,
            "summary": "Candidate evaluation complete",
        }
        self.experiment_manager.write_report(experiment, report_payload)

        promoted = bool(
            evaluation.get("passed")
            and not performance.get("degraded")
            and self._improves_metrics(candidate, production, baseline_metrics)
            and self._within_drawdown(candidate, production)
        )

        if promoted:
            self.registry.promote_model(candidate.version)
            self.retraining_scheduler.mark_run()
            return {"promoted": True, "experiment": experiment, "report": report_payload}

        self.retraining_scheduler.mark_run()
        return {"promoted": False, "experiment": experiment, "report": report_payload, "reason": "failed safety checks"}

    def _improves_metrics(self, candidate: ModelRecord, production: ModelRecord, baseline_metrics: dict[str, float]) -> bool:
        candidate_metrics = {**candidate.validation_metrics, **candidate.backtest_metrics}
        production_metrics = {**production.validation_metrics, **production.backtest_metrics}
        for metric_name, baseline_value in baseline_metrics.items():
            if metric_name not in candidate_metrics or metric_name not in production_metrics:
                continue
            if metric_name == "max_drawdown":
                continue
            if candidate_metrics[metric_name] <= production_metrics[metric_name]:
                return False
        return True

    def _within_drawdown(self, candidate: ModelRecord, production: ModelRecord) -> bool:
        candidate_drawdown = candidate.backtest_metrics.get("max_drawdown", 0.0)
        production_drawdown = production.backtest_metrics.get("max_drawdown", 0.0)
        return candidate_drawdown <= self.drawdown_limit and candidate_drawdown <= production_drawdown + self.drawdown_limit
