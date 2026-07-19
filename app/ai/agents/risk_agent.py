from __future__ import annotations

from app.ai.agents.base_agent import BaseAgent


class RiskAgent(BaseAgent):
    """Monitor risk conditions and emit suggestions."""

    name = "risk_agent"

    def evaluate(self, context) -> dict[str, object]:
        return {"agent": self.name, "status": "evaluated", "result": {"suggestion": "reduce_exposure"}}
