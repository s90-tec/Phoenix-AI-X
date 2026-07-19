import unittest
from unittest.mock import patch

import pandas as pd

from app.paper.live_paper_trader import PaperTrader
from app.portfolio.portfolio import Portfolio


class LivePaperTraderTests(unittest.TestCase):
    def test_buy_signal_saves_trade(self) -> None:
        trader = PaperTrader(db_engine=object())
        trader.portfolio = Portfolio()

        df = pd.DataFrame(
            {
                "timestamp": [pd.Timestamp("2026-07-18 12:00:00")],
                "open": [100.0],
                "high": [101.0],
                "low": [99.0],
                "close": [100.0],
                "volume": [1.0],
            }
        )

        with patch.object(trader, "_fetch_ohlcv", return_value=df):
            with patch.object(trader, "_get_signal", return_value=("BUY", 0.95)):
                with patch.object(trader.execution_trader, "execute") as mock_execute:
                    trader.step()

        self.assertEqual(mock_execute.call_count, 1)
        self.assertEqual(mock_execute.call_args.kwargs["signal"], "BUY")


if __name__ == "__main__":
    unittest.main()
