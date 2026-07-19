import logging
import unittest
from unittest.mock import Mock

import pandas as pd

from app.paper.live_runner import LiveRunner


class LiveRunnerTests(unittest.TestCase):
    def test_successful_iteration(self) -> None:
        market_data = Mock()
        market_data.fetch_candles.return_value = pd.DataFrame(
            {
                "timestamp": [1],
                "open": [100.0],
                "high": [101.0],
                "low": [99.0],
                "close": [100.0],
                "volume": [10.0],
            }
        )

        feature_engine = Mock()
        feature_engine.get_latest_feature_row.return_value = pd.DataFrame({"EMA20": [1.0]})

        predictor = Mock()
        predictor.predict_signal.return_value = ("BUY", 0.95)

        risk_manager = Mock()
        risk_manager.manage_risk.return_value = "BUY"

        trader = Mock()

        runner = LiveRunner(
            market_data=market_data,
            feature_engine=feature_engine,
            predictor=predictor,
            risk_manager=risk_manager,
            trader=trader,
            logger_instance=logging.getLogger("test"),
        )

        runner.run_once()

        trader.execute.assert_called_once()

    def test_hold_signal(self) -> None:
        market_data = Mock()
        market_data.fetch_candles.return_value = pd.DataFrame({"timestamp": [1], "open": [100.0], "high": [101.0], "low": [99.0], "close": [100.0], "volume": [10.0]})
        feature_engine = Mock()
        feature_engine.get_latest_feature_row.return_value = pd.DataFrame({"EMA20": [1.0]})
        predictor = Mock()
        predictor.predict_signal.return_value = ("HOLD", 0.95)
        risk_manager = Mock()
        risk_manager.manage_risk.return_value = "HOLD"
        trader = Mock()

        runner = LiveRunner(market_data, feature_engine, predictor, risk_manager, trader)
        runner.run_once()

        trader.execute.assert_not_called()

    def test_predictor_failure(self) -> None:
        market_data = Mock()
        market_data.fetch_candles.return_value = pd.DataFrame({"timestamp": [1], "open": [100.0], "high": [101.0], "low": [99.0], "close": [100.0], "volume": [10.0]})
        feature_engine = Mock()
        feature_engine.get_latest_feature_row.return_value = pd.DataFrame({"EMA20": [1.0]})
        predictor = Mock()
        predictor.predict_signal.side_effect = RuntimeError("model failure")
        risk_manager = Mock()
        trader = Mock()

        runner = LiveRunner(market_data, feature_engine, predictor, risk_manager, trader)
        with self.assertRaises(RuntimeError):
            runner.run_once()

    def test_exchange_failure(self) -> None:
        market_data = Mock()
        market_data.fetch_candles.side_effect = RuntimeError("exchange failure")
        feature_engine = Mock()
        predictor = Mock()
        risk_manager = Mock()
        trader = Mock()

        runner = LiveRunner(market_data, feature_engine, predictor, risk_manager, trader)
        with self.assertRaises(RuntimeError):
            runner.run_once()

    def test_keyboard_interrupt(self) -> None:
        market_data = Mock()
        market_data.fetch_candles.side_effect = KeyboardInterrupt()
        feature_engine = Mock()
        predictor = Mock()
        risk_manager = Mock()
        trader = Mock()

        runner = LiveRunner(market_data, feature_engine, predictor, risk_manager, trader)
        with self.assertRaises(KeyboardInterrupt):
            runner.run_once()


if __name__ == "__main__":
    unittest.main()
