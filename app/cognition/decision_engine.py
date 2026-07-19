"""Market-aware decision facade."""

from __future__ import annotations

from app.cognition.reasoner import ReasonedAction, Reasoner


class DecisionEngine:
    """Adds current market regime context before explainable ranking."""

    def __init__(self, reasoner: Reasoner | None = None) -> None:
        self.reasoner = reasoner or Reasoner()

    def decide(self, actions: list[dict[str, object]], *, market_regime: str = "unknown") -> list[ReasonedAction]:
        enriched = []
        for action in actions:
            candidate = dict(action)
            candidate["regime_fit"] = float(candidate.get("regime_fit", candidate.get("regime_fitness", 0.5)))
            candidate["market_regime"] = market_regime
            enriched.append(candidate)
        return self.reasoner.evaluate(enriched)
