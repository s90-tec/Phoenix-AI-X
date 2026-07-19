"""Experiment metric analysis."""

from __future__ import annotations

from typing import Any


class ResultAnalyzer:
    """Normalizes performance metrics and compares an experiment to baseline."""

    METRICS = ("sharpe", "sortino", "win_rate", "drawdown", "profit_factor", "recovery_factor", "expectancy")

    def analyze(self, metrics: dict[str, float], *, baseline: dict[str, float] | None = None) -> dict[str, Any]:
        values = {name: float(metrics.get(name, 0.0)) for name in self.METRICS}
        score = (values["sharpe"] * 0.30 + values["sortino"] * 0.20 + values["win_rate"] * 0.15 + values["profit_factor"] * 0.15 + values["recovery_factor"] * 0.10 + values["expectancy"] * 0.10 - values["drawdown"] * 0.20)
        comparison = {name: round(value - float(baseline.get(name, 0.0)), 10) for name, value in values.items() if baseline and name in baseline}
        return {"metrics": values, "score": score, "comparison": comparison}
