from __future__ import annotations

from app.ai.agents.base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """Generate hypotheses and candidate ideas."""

    name = "research_agent"

    def analyze(self, context) -> dict[str, object]:
        return {"agent": self.name, "status": "analyzed", "result": {"hypothesis": "Momentum may improve in high-volatility regimes"}}
