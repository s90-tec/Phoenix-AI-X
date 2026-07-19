import unittest

import pandas as pd

from app.strategy.strategies.ai_strategy import AIStrategy


class AIStrategyTests(unittest.TestCase):
    def test_ai_strategy_wraps_predictor(self) -> None:
        strategy = AIStrategy()
        features = pd.DataFrame(
            [{"EMA20": 10.0, "EMA50": 8.0, "MACD": 1.0, "MACD_Signal": 0.2, "RSI": 40.0}]
        )
        signal = strategy.generate_signal(features)
        self.assertIn(signal.signal, {"BUY", "SELL", "HOLD"})


if __name__ == "__main__":
    unittest.main()
