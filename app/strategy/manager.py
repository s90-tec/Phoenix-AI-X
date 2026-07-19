from __future__ import annotations

from typing import Any, Sequence

import pandas as pd

from app.strategy.base import BaseStrategy, Signal, StrategyResult


class StrategyManager:
    """Coordinate one or many strategies with a configurable voting method."""

    def __init__(self, strategies: Sequence[BaseStrategy] | None = None, voting_method: str = "majority") -> None:
        self.strategies = list(strategies or [])
        self.voting_method = voting_method

    def add_strategy(self, strategy: BaseStrategy) -> None:
        """Append a strategy to the active set."""
        self.strategies.append(strategy)

    def clear(self) -> None:
        """Remove all active strategies."""
        self.strategies.clear()

    def run(self, features: pd.DataFrame, symbol: str = "") -> StrategyResult:
        """Run all active strategies and aggregate to a single result."""
        if not self.strategies:
            return StrategyResult(strategy_name="manager", signal="HOLD", confidence=0.0, reason="No strategies configured")

        signals = [strategy.generate_signal(features) for strategy in self.strategies]
        valid_signals = [signal for signal in signals if signal.signal in {"BUY", "SELL", "HOLD"}]
        if not valid_signals:
            return StrategyResult(strategy_name="manager", signal="HOLD", confidence=0.0, reason="No valid signals")

        if self.voting_method == "weighted":
            return self._weighted_vote(valid_signals, symbol)
        if self.voting_method == "highest_confidence":
            return self._highest_confidence(valid_signals, symbol)
        return self._majority_vote(valid_signals, symbol)

    def _majority_vote(self, signals: Sequence[Signal], symbol: str) -> StrategyResult:
        buy_votes = sum(1 for signal in signals if signal.signal == "BUY")
        sell_votes = sum(1 for signal in signals if signal.signal == "SELL")
        if buy_votes > sell_votes and buy_votes > 0:
            signal = max((item for item in signals if item.signal == "BUY"), key=lambda item: item.confidence)
            return StrategyResult(strategy_name="manager", signal="BUY", confidence=signal.confidence, reason=signal.reason, metadata={"symbol": symbol, "strategy_name": signal.strategy_name})
        if sell_votes > buy_votes and sell_votes > 0:
            signal = max((item for item in signals if item.signal == "SELL"), key=lambda item: item.confidence)
            return StrategyResult(strategy_name="manager", signal="SELL", confidence=signal.confidence, reason=signal.reason, metadata={"symbol": symbol, "strategy_name": signal.strategy_name})
        return StrategyResult(strategy_name="manager", signal="HOLD", confidence=0.0, reason="No clear majority", metadata={"symbol": symbol})

    def _weighted_vote(self, signals: Sequence[Signal], symbol: str) -> StrategyResult:
        weights = {signal.strategy_name: 1.0 for signal in signals}
        if not weights:
            return StrategyResult(strategy_name="manager", signal="HOLD", confidence=0.0, reason="No signals")
        buy_score = sum(weights.get(signal.strategy_name, 1.0) for signal in signals if signal.signal == "BUY")
        sell_score = sum(weights.get(signal.strategy_name, 1.0) for signal in signals if signal.signal == "SELL")
        if buy_score > sell_score:
            return StrategyResult(strategy_name="manager", signal="BUY", confidence=max(signal.confidence for signal in signals if signal.signal == "BUY"), reason="Weighted vote", metadata={"symbol": symbol})
        if sell_score > buy_score:
            return StrategyResult(strategy_name="manager", signal="SELL", confidence=max(signal.confidence for signal in signals if signal.signal == "SELL"), reason="Weighted vote", metadata={"symbol": symbol})
        return StrategyResult(strategy_name="manager", signal="HOLD", confidence=0.0, reason="Tie in weighted vote", metadata={"symbol": symbol})

    def _highest_confidence(self, signals: Sequence[Signal], symbol: str) -> StrategyResult:
        if not signals:
            return StrategyResult(strategy_name="manager", signal="HOLD", confidence=0.0, reason="No signals", metadata={"symbol": symbol})
        best = max(signals, key=lambda signal: signal.confidence)
        return StrategyResult(strategy_name="manager", signal=best.signal, confidence=best.confidence, reason=best.reason, metadata={"symbol": symbol, "strategy_name": best.strategy_name})
