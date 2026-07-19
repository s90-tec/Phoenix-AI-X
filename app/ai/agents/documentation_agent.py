from __future__ import annotations

from app.ai.agents.base_agent import BaseAgent


class DocumentationAgent(BaseAgent):
    """Generate documentation artifacts for the platform."""

    name = "documentation_agent"

    def report(self, context) -> dict[str, object]:
        return {"agent": self.name, "status": "reported", "result": {"artifact": "architecture.md"}}
