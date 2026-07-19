from __future__ import annotations

from typing import Any

from app.strategy.base import BaseStrategy


class StrategyRegistry:
    """Register and retrieve strategies by name."""

    def __init__(self) -> None:
        self._strategies: dict[str, type[BaseStrategy]] = {}

    def register(self, strategy_cls: type[BaseStrategy], *, override: bool = False) -> None:
        """Register a strategy class by its name."""
        if not issubclass(strategy_cls, BaseStrategy):
            raise TypeError("Registered strategies must inherit BaseStrategy")
        name = strategy_cls.name
        if name in self._strategies and not override:
            raise ValueError(f"Strategy {name} already registered")
        self._strategies[name] = strategy_cls

    def unregister(self, name: str) -> None:
        """Remove a strategy from the registry."""
        self._strategies.pop(name, None)

    def get(self, name: str) -> type[BaseStrategy]:
        """Return a registered strategy class."""
        try:
            return self._strategies[name]
        except KeyError as exc:
            raise KeyError(f"Unknown strategy: {name}") from exc

    def list(self) -> list[str]:
        """Return the registered strategy names."""
        return sorted(self._strategies)

    def metadata(self) -> dict[str, dict[str, Any]]:
        """Return strategy metadata for the registry."""
        return {name: self.get(name)().get_metadata() for name in self.list()}
