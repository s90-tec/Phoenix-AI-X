from __future__ import annotations

import logging
from typing import Optional

import ccxt
import numpy as np
import pandas as pd
import ta

from app.config import TIMEFRAME
from app.exchange.market_data import MarketData

logger = logging.getLogger(__name__)


class FeatureEngine:
    """Generate a real-time feature vector from the latest Binance candles."""

    def __init__(self, exchange: Optional[ccxt.Exchange] = None, symbol: str = "BTC/USDT") -> None:
        self.market_data = MarketData(exchange=exchange)
        self.symbol = symbol
        self.timeframe = TIMEFRAME

    def _fetch_candles(self, limit: int = 250) -> pd.DataFrame:
        return self.market_data.fetch_candles(
            symbol=self.symbol,
            timeframe=self.timeframe,
            limit=limit,
        )

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        features = df.copy()

        if len(features) < 2:
            features["EMA20"] = features["close"]
            features["EMA50"] = features["close"]
            features["EMA100"] = features["close"]
            features["EMA200"] = features["close"]
            features["RSI"] = 0.0
            features["MACD"] = 0.0
            features["MACD_Signal"] = 0.0
            features["MACD_Hist"] = 0.0
            features["ATR"] = 0.0
            features["ADX"] = 0.0
            features["BB_Upper"] = features["close"]
            features["BB_Lower"] = features["close"]
            features["BB_Width"] = 0.0
            features["Volume_MA"] = features["volume"]
            features["Return1"] = 0.0
            features["Return5"] = 0.0
            return features

        min_periods = max(2, min(len(features), 14))

        features["EMA20"] = ta.trend.ema_indicator(features["close"], window=min(20, len(features)))
        features["EMA50"] = ta.trend.ema_indicator(features["close"], window=min(50, len(features)))
        features["EMA100"] = ta.trend.ema_indicator(features["close"], window=min(100, len(features)))
        features["EMA200"] = ta.trend.ema_indicator(features["close"], window=min(200, len(features)))

        features["RSI"] = ta.momentum.rsi(features["close"], window=min(14, len(features)))

        macd = ta.trend.MACD(features["close"])
        features["MACD"] = macd.macd()
        features["MACD_Signal"] = macd.macd_signal()
        features["MACD_Hist"] = macd.macd_diff()

        try:
            features["ATR"] = ta.volatility.average_true_range(
                features["high"],
                features["low"],
                features["close"],
                window=min_periods,
            )
        except Exception:
            features["ATR"] = pd.Series(0.0, index=features.index)

        try:
            features["ADX"] = ta.trend.adx(features["high"], features["low"], features["close"], window=min_periods)
        except Exception:
            features["ADX"] = pd.Series(0.0, index=features.index)

        bb = ta.volatility.BollingerBands(features["close"])
        features["BB_Upper"] = bb.bollinger_hband()
        features["BB_Lower"] = bb.bollinger_lband()
        features["BB_Width"] = bb.bollinger_wband()

        features["Volume_MA"] = features["volume"].rolling(min(20, len(features))).mean()
        features["Return1"] = features["close"].pct_change(1)
        features["Return5"] = features["close"].pct_change(5)

        return features.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    def build_features(self, limit: int = 250) -> pd.DataFrame:
        """Build and return the full feature DataFrame from live market data."""
        try:
            candles = self._fetch_candles(limit=limit)
            features = self._calculate_indicators(candles)
            cleaned = features.dropna().reset_index(drop=True)
            if cleaned.empty:
                return pd.DataFrame([features.iloc[-1].fillna(0.0)])
            return cleaned
        except Exception as exc:  # pragma: no cover - runtime robustness
            logger.exception("Failed to build realtime features: %s", exc)
            raise

    def get_latest_feature_row(self, limit: int = 250) -> pd.DataFrame:
        """Return the latest feature row as a single-row DataFrame."""
        features = self.build_features(limit=limit)
        if features.empty:
            raise ValueError("No features could be generated from the latest market data")

        latest = features.iloc[[-1]].copy()
        latest = latest.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        return latest[[
            "EMA20",
            "EMA50",
            "EMA100",
            "EMA200",
            "RSI",
            "MACD",
            "MACD_Signal",
            "MACD_Hist",
            "ATR",
            "ADX",
            "Return1",
            "Return5",
            "Volume_MA",
        ]]


def get_latest_features() -> pd.DataFrame:
    """Convenience function returning the latest real-time feature row."""
    engine = FeatureEngine()
    return engine.get_latest_feature_row()
