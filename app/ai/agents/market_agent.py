from __future__ import annotations

from app.ai.agents.base_agent import BaseAgent


class MarketAgent(BaseAgent):
    """Observe the market and emit structured observations."""

    name = "market_agent"

    def observe(self, context) -> dict[str, object]:
        context.market_state = {"trend": context.market_state.get("trend", "neutral"), "observed": True}
        return {"agent": self.name, "status": "observed", "result": context.market_state}

    def analyze(self, context) -> dict[str, object]:
        return {"agent": self.name, "status": "analyzed", "result": {"regime": "trend"}}
