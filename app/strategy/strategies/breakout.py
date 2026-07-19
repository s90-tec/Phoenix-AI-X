from __future__ import annotations

import pandas as pd

from app.strategy.base import BaseStrategy, Signal


class BreakoutStrategy(BaseStrategy):
    """Simple breakout strategy based on price action relative to Bollinger Bands."""

    name = "breakout"

    def generate_signal(self, features: pd.DataFrame) -> Signal:
        if features.empty:
            return Signal(strategy_name=self.name, symbol="", signal="HOLD", confidence=0.0, timestamp="", reason="No feature data", metadata={})
        latest = features.iloc[-1]
        if latest["close"] > latest["BB_Upper"]:
            return Signal(strategy_name=self.name, symbol="", signal="BUY", confidence=0.68, timestamp="", reason="Price above upper Bollinger Band", metadata={})
        if latest["close"] < latest["BB_Lower"]:
            return Signal(strategy_name=self.name, symbol="", signal="SELL", confidence=0.68, timestamp="", reason="Price below lower Bollinger Band", metadata={})
        return Signal(strategy_name=self.name, symbol="", signal="HOLD", confidence=0.2, timestamp="", reason="Inside Bollinger Bands", metadata={})
