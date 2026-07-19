from __future__ import annotations

from typing import Any, List

from app.ai.context import AIContext
from app.ai.kernel import AIKernel


class AIOrchestrator:
    """Coordinate sequential or parallel agent workflows."""

    def __init__(self, kernel: AIKernel) -> None:
        self.kernel = kernel

    def execute_sequential(self, agents: List[Any], context: AIContext) -> List[dict[str, Any]]:
        results = []
        for agent in agents:
            self.kernel.context = context
            result = agent.run_cycle(context)
            results.append(result)
        return results

    def execute_parallel(self, agents: List[Any], context: AIContext) -> List[dict[str, Any]]:
        return self.execute_sequential(agents, context)
