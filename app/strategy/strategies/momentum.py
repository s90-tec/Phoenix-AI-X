from __future__ import annotations

import pandas as pd

from app.strategy.base import BaseStrategy, Signal


class MomentumStrategy(BaseStrategy):
    """Momentum strategy based on the latest return."""

    name = "momentum"

    def generate_signal(self, features: pd.DataFrame) -> Signal:
        if features.empty:
            return Signal(strategy_name=self.name, symbol="", signal="HOLD", confidence=0.0, timestamp="", reason="No feature data", metadata={})
        latest = features.iloc[-1]
        if latest["Return1"] > 0.01:
            return Signal(strategy_name=self.name, symbol="", signal="BUY", confidence=0.7, timestamp="", reason="Positive short-term momentum", metadata={})
        if latest["Return1"] < -0.01:
            return Signal(strategy_name=self.name, symbol="", signal="SELL", confidence=0.7, timestamp="", reason="Negative short-term momentum", metadata={})
        return Signal(strategy_name=self.name, symbol="", signal="HOLD", confidence=0.2, timestamp="", reason="Momentum neutral", metadata={})
