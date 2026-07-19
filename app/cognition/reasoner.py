"""Explainable symbolic comparison of action alternatives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ReasonedAction:
    name: str
    score: float
    confidence: float
    explanation: str
    evidence: dict[str, Any] = field(default_factory=dict)


class Reasoner:
    """Ranks hypotheses/actions using transparent weighted facts."""

    def evaluate(self, alternatives: list[dict[str, Any]]) -> list[ReasonedAction]:
        actions: list[ReasonedAction] = []
        for alternative in alternatives:
            confidence = float(alternative.get("confidence", 0.0))
            expected_return = float(alternative.get("expected_return", 0.0))
            risk = float(alternative.get("risk", 0.0))
            historical = float(alternative.get("historical_performance", 0.0))
            resources = float(alternative.get("resource_cost", 0.0))
            regime_fit = float(alternative.get("regime_fit", 0.5))
            score = expected_return * 0.35 + confidence * 0.25 + historical * 0.20 + regime_fit * 0.15 - risk * 0.30 - resources * 0.05
            explanation = f"Selected from expected return ({expected_return:.2f}), confidence ({confidence:.2f}), historical performance ({historical:.2f}), regime fit ({regime_fit:.2f}), risk ({risk:.2f}), and resource cost ({resources:.2f})."
            actions.append(ReasonedAction(name=str(alternative["name"]), score=score, confidence=confidence, explanation=explanation, evidence=dict(alternative)))
        return sorted(actions, key=lambda action: action.score, reverse=True)

    def select(self, alternatives: list[dict[str, Any]]) -> ReasonedAction:
        ranked = self.evaluate(alternatives)
        if not ranked:
            raise ValueError("At least one alternative is required")
        return ranked[0]
