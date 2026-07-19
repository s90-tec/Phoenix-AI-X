from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class Signal:
    """Immutable signal emitted by a strategy."""

    strategy_name: str
    symbol: str
    signal: str
    confidence: float
    timestamp: str
    reason: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class TradeDecision:
    """Structured decision suitable for paper trading or backtesting."""

    signal: Signal
    action: str


@dataclass(frozen=True)
class StrategyResult:
    """Aggregated outcome from a strategy execution."""

    strategy_name: str
    signal: str
    confidence: float
    reason: str
    metadata: dict[str, Any] | None = None


class BaseStrategy:
    """Abstract interface for all strategies in the framework."""

    name: str = "base"

    def prepare(self, features: pd.DataFrame) -> pd.DataFrame:
        """Normalize or enrich features before generating a signal."""
        return features

    def generate_signal(self, features: pd.DataFrame) -> Signal:
        """Return a Signal using the provided feature frame."""
        raise NotImplementedError

    def validate(self, signal: Signal) -> bool:
        """Validate a generated signal before it is used by the manager."""
        return signal.signal in {"BUY", "SELL", "HOLD"}

    def get_metadata(self) -> dict[str, Any]:
        """Expose descriptive metadata for the strategy."""
        return {"name": self.name}
