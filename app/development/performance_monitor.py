from __future__ import annotations

from typing import Any


class PerformanceMonitor:
    """Identify regression signals in validation and backtest metrics."""

    def __init__(self, *, degradation_threshold: float = 0.1, drawdown_limit: float = 0.2) -> None:
        self.degradation_threshold = degradation_threshold
        self.drawdown_limit = drawdown_limit

    def analyze(self, current_metrics: dict[str, float], baseline_metrics: dict[str, float]) -> dict[str, Any]:
        issues: list[str] = []
        for metric_name, baseline_value in baseline_metrics.items():
            if metric_name not in current_metrics:
                continue
            current_value = current_metrics[metric_name]
            if metric_name == "max_drawdown":
                if current_value > baseline_value + self.degradation_threshold or current_value > self.drawdown_limit:
                    issues.append(metric_name)
            else:
                tolerance = max(abs(baseline_value) * self.degradation_threshold, self.degradation_threshold)
                if current_value < baseline_value - tolerance:
                    issues.append(metric_name)

        suggestions = self._suggest_improvements(issues)
        return {
            "degraded": bool(issues),
            "issues": issues,
            "suggestions": suggestions,
        }

    def _suggest_improvements(self, issues: list[str]) -> list[str]:
        suggestions: list[str] = []
        if "max_drawdown" in issues:
            suggestions.append("Reduce position sizing and tighten risk controls")
        if "sharpe" in issues:
            suggestions.append("Tune hyperparameters to improve reward-to-risk balance")
        if "accuracy" in issues:
            suggestions.append("Expand the training window or enrich features")
        return suggestions
