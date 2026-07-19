import unittest

from app.portfolio.portfolio import Portfolio
from app.risk.risk_manager import RiskManager


class RiskManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.portfolio = Portfolio()
        self.manager = RiskManager(portfolio=self.portfolio)

    def test_buy_allowed(self) -> None:
        self.assertTrue(self.manager.can_execute("BUY", 0.95, "BTC/USDT", 100.0))

    def test_buy_rejected_low_confidence(self) -> None:
        self.assertFalse(self.manager.can_execute("BUY", 0.1, "BTC/USDT", 100.0))

    def test_buy_rejected_open_position(self) -> None:
        self.portfolio.position = "LONG"
        self.assertFalse(self.manager.can_execute("BUY", 0.95, "BTC/USDT", 100.0))

    def test_daily_loss_exceeded(self) -> None:
        self.manager.record_trade_result("BUY", True, 100.0, 0.0, 9000.0, -1200.0)
        self.assertFalse(self.manager.can_execute("BUY", 0.95, "BTC/USDT", 100.0))

    def test_drawdown_exceeded(self) -> None:
        self.manager.record_trade_result("BUY", True, 100.0, 0.0, 8000.0, -2000.0)
        self.assertFalse(self.manager.can_execute("BUY", 0.95, "BTC/USDT", 100.0))

    def test_stop_loss_triggered(self) -> None:
        position = {"entry_price": 100.0}
        self.assertTrue(self.manager.should_exit(position, 95.0))

    def test_take_profit_triggered(self) -> None:
        position = {"entry_price": 100.0}
        self.assertTrue(self.manager.should_exit(position, 115.0))

    def test_position_sizing_calculation(self) -> None:
        size = self.manager.calculate_position_size(10000.0, 0.02, 0.05)
        self.assertEqual(size, 4000.0)


if __name__ == "__main__":
    unittest.main()
