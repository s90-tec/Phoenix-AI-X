from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Any

from app.strategy.base import BaseStrategy
from app.strategy.registry import StrategyRegistry


class StrategyLoader:
    """Load strategy modules dynamically from the strategies package."""

    def __init__(self, registry: StrategyRegistry | None = None) -> None:
        self.registry = registry or StrategyRegistry()

    def discover(self, package: str = "app.strategy.strategies") -> list[type[BaseStrategy]]:
        """Import all strategy modules under the strategies package and register their classes."""
        package_obj = importlib.import_module(package)
        module_path = Path(package_obj.__file__).parent
        discovered: list[type[BaseStrategy]] = []

        for module_info in pkgutil.iter_modules([str(module_path)]):
            if module_info.name.startswith("_"):
                continue
            full_name = f"{package}.{module_info.name}"
            module = importlib.import_module(full_name)
            for _, obj in vars(module).items():
                if isinstance(obj, type) and issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
                    self.registry.register(obj)
                    discovered.append(obj)
        return discovered
