from __future__ import annotations

import pandas as pd

from app.strategy.base import BaseStrategy, Signal


class TrendFollowingStrategy(BaseStrategy):
    """Simple trend-following strategy based on EMA and MACD crossovers."""

    name = "trend_following"

    def generate_signal(self, features: pd.DataFrame) -> Signal:
        if features.empty:
            return Signal(strategy_name=self.name, symbol="", signal="HOLD", confidence=0.0, timestamp="", reason="No feature data", metadata={})

        latest = features.iloc[-1]
        previous = features.iloc[-2] if len(features) > 1 else latest
        ema20_cross = latest["EMA20"] > latest["EMA50"] and previous["EMA20"] <= previous["EMA50"]
        ema20_down_cross = latest["EMA20"] < latest["EMA50"] and previous["EMA20"] >= previous["EMA50"]
        macd_cross = latest["MACD"] > latest["MACD_Signal"] and previous["MACD"] <= previous["MACD_Signal"]
        macd_down_cross = latest["MACD"] < latest["MACD_Signal"] and previous["MACD"] >= previous["MACD_Signal"]
        ema_strength = abs(float(latest["EMA20"] - latest["EMA50"]))
        macd_strength = abs(float(latest["MACD"] - latest["MACD_Signal"]))
        if ema20_cross and macd_cross and ema_strength >= 0.5 and macd_strength >= 0.05:
            return Signal(strategy_name=self.name, symbol="", signal="BUY", confidence=0.85, timestamp="", reason="EMA and MACD bullish crossover", metadata={})
        if ema20_down_cross and macd_down_cross and ema_strength >= 0.5 and macd_strength >= 0.05:
            return Signal(strategy_name=self.name, symbol="", signal="SELL", confidence=0.85, timestamp="", reason="EMA and MACD bearish crossover", metadata={})
        return Signal(strategy_name=self.name, symbol="", signal="HOLD", confidence=0.2, timestamp="", reason="No clear trend crossover", metadata={})
