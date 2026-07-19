import unittest

import pandas as pd

from app.strategy.strategy_engine import StrategyEngine, TrendFollowingStrategy


class StrategyEngineTests(unittest.TestCase):
    def test_buy_signal_generated_on_ema_crossover(self) -> None:
        strategy = TrendFollowingStrategy()
        features = pd.DataFrame(
            [
                {"EMA20": 10.0, "EMA50": 12.0, "MACD": 0.5, "MACD_Signal": 0.8},
                {"EMA20": 13.0, "EMA50": 11.0, "MACD": 0.9, "MACD_Signal": 0.2},
            ]
        )
        signal = strategy.generate_signal(features)
        self.assertEqual(signal.signal, "BUY")
        self.assertGreater(signal.confidence, 0.0)

    def test_sell_signal_generated_on_down_crossover(self) -> None:
        strategy = TrendFollowingStrategy()
        features = pd.DataFrame(
            [
                {"EMA20": 12.0, "EMA50": 10.0, "MACD": 0.8, "MACD_Signal": 0.2},
                {"EMA20": 9.0, "EMA50": 11.0, "MACD": 0.1, "MACD_Signal": 0.5},
            ]
        )
        signal = strategy.generate_signal(features)
        self.assertEqual(signal.signal, "SELL")

    def test_engine_returns_hold_when_no_clear_signal(self) -> None:
        engine = StrategyEngine(strategies=[TrendFollowingStrategy()])
        features = pd.DataFrame(
            [
                {"EMA20": 10.0, "EMA50": 10.0, "MACD": 0.5, "MACD_Signal": 0.5},
                {"EMA20": 10.2, "EMA50": 10.1, "MACD": 0.55, "MACD_Signal": 0.54},
            ]
        )
        signal = engine.generate_signal(features)
        self.assertEqual(signal.signal, "HOLD")


if __name__ == "__main__":
    unittest.main()
