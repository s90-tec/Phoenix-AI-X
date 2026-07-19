from __future__ import annotations

from app.ai.agents.base_agent import BaseAgent


class EvaluationAgent(BaseAgent):
    """Rank strategies and models using evaluation metrics."""

    name = "evaluation_agent"

    def report(self, context) -> dict[str, object]:
        return {"agent": self.name, "status": "reported", "result": {"rank": 1}}
