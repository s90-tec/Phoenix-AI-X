from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.ai.agent_manager import AgentManager
from app.ai.context import AIContext
from app.ai.events import EventBus
from app.ai.memory import AIMemory


class AIKernel:
    """Core container for agent lifecycle, shared context, memory, and events."""

    def __init__(self, *, context: AIContext | None = None, memory: AIMemory | None = None, event_bus: EventBus | None = None, logger: Optional[logging.Logger] = None) -> None:
        self.context = context or AIContext()
        self.memory = memory or AIMemory()
        self.event_bus = event_bus or EventBus()
        self.logger = logger or logging.getLogger("ai.kernel")
        self.agent_manager = AgentManager(event_bus=self.event_bus)
        self.context.memory = self.memory

    def register_agent(self, agent: Any) -> None:
        self.agent_manager.register(agent)
        self.agent_manager.enable(agent.name)
        self.context.agent_results[agent.name] = {"status": "registered"}

    def run_agent(self, name: str) -> Dict[str, Any]:
        result = self.agent_manager.execute(name, self.context)
        self.logger.info("Agent executed", extra={"agent": name})
        return result

    def publish_event(self, event: Any) -> None:
        self.event_bus.publish(event)
        self.context.event_log.append({"event_type": event.event_type, "payload": event.payload})

    def list_agents(self) -> List[str]:
        return self.agent_manager.list()
