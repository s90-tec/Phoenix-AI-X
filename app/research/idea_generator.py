"""Research idea generation informed by system memory."""

from __future__ import annotations

from app.ai.knowledge_base import KnowledgeBase
from app.ai.memory import AIMemory
from app.research.hypothesis import Hypothesis


class IdeaGenerator:
    """Creates novel hypotheses without re-proposing known failed combinations."""

    def __init__(self, *, knowledge_base: KnowledgeBase | None = None, memory: AIMemory | None = None) -> None:
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.memory = memory

    def generate_many(self, *, limit: int = 5, previous_failures: list[str] | None = None, previous_successes: list[str] | None = None, market_regime: str = "unknown") -> list[Hypothesis]:
        failures = {item.casefold() for item in (previous_failures or [])}
        failures.update(self._failed_descriptions())
        successes = previous_successes or []
        indicator_titles = [item.title for item in self.knowledge_base.list_items(kind="indicator")]
        source_pairs = [("RSI", "ADX"), ("EMA", "RSI"), ("ATR", "VWAP"), ("volume", "volatility")]
        hypotheses: list[Hypothesis] = []
        for first, second in source_pairs:
            label = f"{first}+{second}"
            if label.casefold() in failures:
                continue
            knowledge_note = f" Knowledge sources include: {', '.join(indicator_titles[:2])}." if indicator_titles else ""
            success_note = f" Builds on prior success: {successes[0]}." if successes else ""
            hypotheses.append(Hypothesis(description=f"{first} combined with {second} may improve entries in {market_regime} markets.", reasoning=f"Combines complementary signal families.{knowledge_note}{success_note}", expected_outcome="Improved risk-adjusted return versus baseline", priority=1, confidence=0.55))
            if len(hypotheses) >= limit:
                break
        return hypotheses

    def _failed_descriptions(self) -> set[str]:
        if self.memory is None:
            return set()
        return {str(record.content.get("signature", "")).casefold() for record in self.memory.list("research_failure")}
