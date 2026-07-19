from __future__ import annotations

import logging
import time
from typing import Optional

import ccxt
import pandas as pd

logger = logging.getLogger(__name__)


class MarketData:
    """Fetch and normalize OHLCV data from a cryptocurrency exchange."""

    def __init__(self, exchange: Optional[ccxt.Exchange] = None) -> None:
        self.exchange = exchange or ccxt.binance()

    def fetch_candles(
        self,
        symbol: str = "BTC/USDT",
        timeframe: str = "1h",
        limit: int = 250,
        retries: int = 3,
        retry_delay: float = 1.0,
    ) -> pd.DataFrame:
        """Fetch OHLCV candles and return them as a normalized DataFrame."""
        last_error: Optional[Exception] = None

        for attempt in range(1, retries + 1):
            try:
                candles = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                df = pd.DataFrame(
                    candles,
                    columns=["timestamp", "open", "high", "low", "close", "volume"],
                )
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                return df
            except Exception as exc:  # pragma: no cover - defensive runtime path
                last_error = exc
                logger.warning("Attempt %s/%s failed to fetch %s candles: %s", attempt, retries, symbol, exc)
                if attempt < retries:
                    time.sleep(retry_delay)

        raise RuntimeError(f"Unable to fetch market data for {symbol}: {last_error}")
