from __future__ import annotations

from app.ai.agents.base_agent import BaseAgent


class EngineeringAgent(BaseAgent):
    """Detect code quality issues and propose improvements without changing production code."""

    name = "engineering_agent"

    def report(self, context) -> dict[str, object]:
        return {"agent": self.name, "status": "reported", "result": {"proposal": "add_tests"}}
