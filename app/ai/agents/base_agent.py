from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.ai.context import AIContext
from app.ai.kernel import AIKernel


@dataclass
class BaseAgent:
    """Base class for all AI agents with structured lifecycle hooks."""

    name: str = "base_agent"
    kernel: Optional[AIKernel] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        class_name = getattr(type(self), "name", self.name)
        if self.name in {"", "base_agent"} and isinstance(class_name, str) and class_name not in {"", "base_agent"}:
            self.name = class_name

    def initialize(self, context: AIContext) -> Dict[str, Any]:
        return {"agent": self.name, "status": "initialized", "result": {}}

    def observe(self, context: AIContext) -> Dict[str, Any]:
        return {"agent": self.name, "status": "observed", "result": {}}

    def analyze(self, context: AIContext) -> Dict[str, Any]:
        return {"agent": self.name, "status": "analyzed", "result": {}}

    def plan(self, context: AIContext) -> Dict[str, Any]:
        return {"agent": self.name, "status": "planned", "result": {}}

    def execute(self, context: AIContext) -> Dict[str, Any]:
        return {"agent": self.name, "status": "executed", "result": {}}

    def evaluate(self, context: AIContext) -> Dict[str, Any]:
        return {"agent": self.name, "status": "evaluated", "result": {}}

    def report(self, context: AIContext) -> Dict[str, Any]:
        return {"agent": self.name, "status": "reported", "result": {}}

    def shutdown(self, context: AIContext) -> Dict[str, Any]:
        return {"agent": self.name, "status": "shutdown", "result": {}}

    def run_cycle(self, context: AIContext) -> Dict[str, Any]:
        self.initialize(context)
        self.observe(context)
        self.analyze(context)
        self.plan(context)
        self.execute(context)
        self.evaluate(context)
        self.report(context)
        self.shutdown(context)
        return {"agent": self.name or "base_agent", "status": "completed", "result": {"context": context.__dict__}}
