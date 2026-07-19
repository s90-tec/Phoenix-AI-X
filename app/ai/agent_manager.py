from __future__ import annotations

from typing import Any, Dict, List

from app.ai.context import AIContext
from app.ai.events import EventBus


class AgentManager:
    """Register, enable, disable, list, and execute agents."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._agents: Dict[str, Any] = {}
        self._enabled: set[str] = set()
        self.event_bus = event_bus or EventBus()

    def register(self, agent: Any) -> None:
        if agent.name in self._agents:
            raise ValueError(f"Agent {agent.name} already registered")
        self._agents[agent.name] = agent

    def unregister(self, name: str) -> None:
        self._agents.pop(name, None)
        self._enabled.discard(name)

    def enable(self, name: str) -> None:
        if name not in self._agents:
            raise KeyError(f"Unknown agent: {name}")
        self._enabled.add(name)

    def disable(self, name: str) -> None:
        self._enabled.discard(name)

    def list(self) -> List[str]:
        return sorted(self._agents)

    def status(self, name: str) -> Dict[str, Any]:
        return {"name": name, "enabled": name in self._enabled, "registered": name in self._agents}

    def execute(self, name: str, context: AIContext) -> Dict[str, Any]:
        agent = self._agents[name]
        if name not in self._enabled:
            raise RuntimeError(f"Agent {name} is disabled")
        result = agent.run_cycle(context)
        context.agent_results[name] = result
        return result

    def health(self) -> Dict[str, Any]:
        return {"agents": {name: self.status(name) for name in self.list()}}
