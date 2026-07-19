from __future__ import annotations

import pandas as pd

from app.strategy.base import BaseStrategy, Signal


class MeanReversionStrategy(BaseStrategy):
    """Simple mean-reversion strategy using RSI oversold/overbought states."""

    name = "mean_reversion"

    def generate_signal(self, features: pd.DataFrame) -> Signal:
        if features.empty:
            return Signal(strategy_name=self.name, symbol="", signal="HOLD", confidence=0.0, timestamp="", reason="No feature data", metadata={})
        latest = features.iloc[-1]
        if latest["RSI"] <= 30:
            return Signal(strategy_name=self.name, symbol="", signal="BUY", confidence=0.75, timestamp="", reason="RSI oversold", metadata={})
        if latest["RSI"] >= 70:
            return Signal(strategy_name=self.name, symbol="", signal="SELL", confidence=0.75, timestamp="", reason="RSI overbought", metadata={})
        return Signal(strategy_name=self.name, symbol="", signal="HOLD", confidence=0.2, timestamp="", reason="RSI neutral", metadata={})
