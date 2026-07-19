from __future__ import annotations

from app.strategy.base import BaseStrategy
from app.strategy.registry import StrategyRegistry


class StrategyFactory:
    """Instantiate strategies from the registry by name."""

    def __init__(self, registry: StrategyRegistry | None = None) -> None:
        self.registry = registry or StrategyRegistry()

    def create(self, name: str) -> BaseStrategy:
        """Create a strategy instance by name."""
        strategy_cls = self.registry.get(name)
        return strategy_cls()
