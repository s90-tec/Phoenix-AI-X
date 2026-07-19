import unittest
from unittest.mock import Mock

import pandas as pd

from app.exchange.market_data import MarketData


class MarketDataTests(unittest.TestCase):
    def test_fetch_candles_returns_dataframe(self) -> None:
        exchange = Mock()
        exchange.fetch_ohlcv.return_value = [
            [1710000000000, 100.0, 101.0, 99.0, 100.0, 10.0],
            [1710003600000, 101.0, 102.0, 100.0, 101.0, 11.0],
        ]

        market_data = MarketData(exchange=exchange)
        df = market_data.fetch_candles(symbol="BTC/USDT", timeframe="1h", limit=2, retries=1)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(list(df.columns), ["timestamp", "open", "high", "low", "close", "volume"])
        self.assertEqual(len(df), 2)


if __name__ == "__main__":
    unittest.main()
