from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import pandas as pd

from app.strategy.strategies.trend_following import TrendFollowingStrategy


@dataclass(frozen=True)
class Signal:
    """Immutable outcome emitted by a strategy."""

    strategy_name: str
    symbol: str
    signal: str
    confidence: float
    timestamp: str
    reason: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class TradeDecision:
    """Decision object suitable for execution or backtesting."""

    signal: Signal
    action: str


@dataclass(frozen=True)
class StrategyResult:
    """Aggregated strategy execution result."""

    strategy_name: str
    signal: str
    confidence: float
    reason: str
    metadata: dict[str, Any] | None = None


class BaseStrategy:
    """Abstract interface for all trading strategies."""

    name: str = "base"

    def prepare(self, features: pd.DataFrame) -> pd.DataFrame:
        """Normalize or enrich features before signaling."""
        return features

    def generate_signal(self, features: pd.DataFrame) -> Signal:
        """Generate a single strategy signal from feature data."""
        raise NotImplementedError

    def validate(self, signal: Signal) -> bool:
        """Validate a generated signal before it is used by the manager."""
        return signal.signal in {"BUY", "SELL", "HOLD"}

    def get_metadata(self) -> dict[str, Any]:
        """Return descriptive metadata for the strategy."""
        return {"name": self.name}


class StrategyEngine:
    """Compatibility wrapper for the historical strategy engine interface."""

    def __init__(self, strategies: Sequence[BaseStrategy]) -> None:
        self.strategies = list(strategies)

    def generate_signal(self, features: pd.DataFrame) -> Signal:
        if not self.strategies:
            return Signal(strategy_name="engine", symbol="", signal="HOLD", confidence=0.0, timestamp="", reason="No strategies configured", metadata={})

        results = [strategy.generate_signal(features) for strategy in self.strategies]
        buy_votes = sum(1 for item in results if item.signal == "BUY")
        sell_votes = sum(1 for item in results if item.signal == "SELL")
        if buy_votes > sell_votes and buy_votes > 0:
            best = max((item for item in results if item.signal == "BUY"), key=lambda item: item.confidence)
            return best
        if sell_votes > buy_votes and sell_votes > 0:
            best = max((item for item in results if item.signal == "SELL"), key=lambda item: item.confidence)
            return best
        return Signal(strategy_name="engine", symbol="", signal="HOLD", confidence=0.0, timestamp="", reason="No clear consensus", metadata={})