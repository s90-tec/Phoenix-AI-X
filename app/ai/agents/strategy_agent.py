from __future__ import annotations

from app.ai.agents.base_agent import BaseAgent


class StrategyAgent(BaseAgent):
    """Create and mutate candidate strategy configurations."""

    name = "strategy_agent"

    def plan(self, context) -> dict[str, object]:
        return {"agent": self.name, "status": "planned", "result": {"candidate_strategy": "trend_following"}}
