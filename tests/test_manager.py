import unittest

import pandas as pd

from app.strategy.base import Signal
from app.strategy.manager import StrategyManager
from app.strategy.strategies.trend_following import TrendFollowingStrategy
from app.strategy.strategies.mean_reversion import MeanReversionStrategy


class StrategyManagerTests(unittest.TestCase):
    def test_majority_voting(self) -> None:
        manager = StrategyManager([TrendFollowingStrategy(), MeanReversionStrategy()], voting_method="majority")
        features = pd.DataFrame(
            [{"EMA20": 10.0, "EMA50": 8.0, "MACD": 1.0, "MACD_Signal": 0.2, "RSI": 80.0}]
        )
        result = manager.run(features)
        self.assertEqual(result.signal, "SELL")

    def test_weighted_voting(self) -> None:
        manager = StrategyManager([TrendFollowingStrategy(), MeanReversionStrategy()], voting_method="weighted")
        features = pd.DataFrame(
            [{"EMA20": 10.0, "EMA50": 8.0, "MACD": 1.0, "MACD_Signal": 0.2, "RSI": 80.0}]
        )
        result = manager.run(features)
        self.assertEqual(result.signal, "SELL")


if __name__ == "__main__":
    unittest.main()
