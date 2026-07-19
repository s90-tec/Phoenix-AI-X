import unittest

from sqlalchemy import create_engine

from app.analytics.analytics import AnalyticsEngine
from app.database.database import Base, Trade
from app.database.repository import TradeRepository


class AnalyticsEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.repository = TradeRepository(self.engine)
        self.analytics = AnalyticsEngine(self.repository)

    def tearDown(self) -> None:
        Base.metadata.drop_all(self.engine)

    def _add_trade(self, timestamp: str, pnl: float, balance: float) -> None:
        self.repository.save_trade(
            timestamp=timestamp,
            symbol="BTC/USDT",
            side="BUY",
            price=100.0,
            quantity=1.0,
            confidence=0.9,
            pnl=pnl,
            balance=balance,
        )

    def test_empty_repository(self) -> None:
        self.assertEqual(self.analytics.get_trade_count(), 0)
        self.assertEqual(self.analytics.get_total_pnl(), 0.0)
        self.assertEqual(self.analytics.get_win_rate(), 0.0)
        self.assertEqual(self.analytics.get_profit_factor(), 0.0)
        self.assertEqual(self.analytics.get_max_drawdown(), 0.0)
        self.assertEqual(self.analytics.get_sharpe_ratio(), 0.0)
        self.assertEqual(self.analytics.generate_summary()["trade_count"], 0)

    def test_single_profitable_trade(self) -> None:
        self._add_trade("2026-07-18 10:00:00", 100.0, 1100.0)
        self.assertEqual(self.analytics.get_total_pnl(), 100.0)
        self.assertEqual(self.analytics.get_win_rate(), 100.0)
        self.assertEqual(self.analytics.get_profit_factor(), float("inf"))
        self.assertEqual(self.analytics.get_trade_count(), 1)

    def test_losing_trade(self) -> None:
        self._add_trade("2026-07-18 10:00:00", -50.0, 950.0)
        self.assertEqual(self.analytics.get_total_pnl(), -50.0)
        self.assertEqual(self.analytics.get_win_rate(), 0.0)
        self.assertEqual(self.analytics.get_profit_factor(), 0.0)

    def test_multiple_trades(self) -> None:
        self._add_trade("2026-07-18 10:00:00", 100.0, 1100.0)
        self._add_trade("2026-07-18 11:00:00", -50.0, 1050.0)
        self._add_trade("2026-07-18 12:00:00", 75.0, 1125.0)
        self.assertEqual(self.analytics.get_trade_count(), 3)
        self.assertEqual(self.analytics.get_total_pnl(), 125.0)
        self.assertEqual(self.analytics.get_win_rate(), 66.67)
        self.assertEqual(self.analytics.get_average_win(), 87.5)
        self.assertEqual(self.analytics.get_average_loss(), -50.0)

    def test_drawdown_and_summary(self) -> None:
        self._add_trade("2026-07-18 10:00:00", -50.0, 950.0)
        self._add_trade("2026-07-18 11:00:00", -25.0, 925.0)
        self._add_trade("2026-07-18 12:00:00", 100.0, 1025.0)
        summary = self.analytics.generate_summary()
        self.assertGreaterEqual(summary["drawdown"], 0.0)
        self.assertEqual(summary["trade_count"], 3)


if __name__ == "__main__":
    unittest.main()
