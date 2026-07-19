"""Default end-to-end research workflow."""

from __future__ import annotations

from app.research.hypothesis import Hypothesis
from app.research.lab import ResearchLab


class ResearchPipeline:
    """Executes the standard hypothesis-to-published-research lifecycle."""

    def __init__(self, *, lab: ResearchLab) -> None:
        self.lab = lab

    def run(self, *, hypothesis: Hypothesis, metrics: dict[str, float] | None = None, baseline: dict[str, float] | None = None) -> dict[str, object]:
        self.lab.register_hypothesis(hypothesis)
        features, strategies = self.lab.prepare_candidates()
        experiment_id = f"research-{hypothesis.id}"
        self.lab.queue_experiment(experiment_id, hypothesis=hypothesis, expected_value=hypothesis.confidence, payload={"signature": hypothesis.description, "features": [feature.name for feature in features], "strategies": [strategy.name for strategy in strategies]})
        self.lab.start_next()
        result = self.lab.complete(experiment_id, metrics or {"sharpe": hypothesis.confidence, "sortino": hypothesis.confidence, "win_rate": 0.5, "profit_factor": 1.1, "recovery_factor": 1.0, "expectancy": 0.05, "drawdown": 0.05}, baseline=baseline)
        result["hypothesis_id"] = hypothesis.id
        return self.lab.publish(result)
