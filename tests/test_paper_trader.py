import os
import tempfile
import unittest
from unittest.mock import Mock

from app.database.database import create_database
from app.database.repository import TradeRepository
from app.paper.trader import PaperTrader
from app.portfolio.portfolio import Portfolio
from app.risk.risk_manager import RiskManager


class PaperTraderTests(unittest.TestCase):
    def test_buy_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "trader.db")
            engine = create_database(db_path)
            repository = TradeRepository(engine)
            portfolio = Portfolio()
            trader = PaperTrader(portfolio=portfolio, repository=repository, risk_manager=RiskManager())

            result = trader.execute(signal="BUY", price=100.0, confidence=0.95, symbol="BTC/USDT")

            self.assertTrue(result.executed)
            self.assertEqual(result.signal, "BUY")
            self.assertEqual(portfolio.position, "LONG")
            self.assertIsNotNone(result.trade)

    def test_sell_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "trader.db")
            engine = create_database(db_path)
            repository = TradeRepository(engine)
            portfolio = Portfolio()
            portfolio.buy(100.0)
            trader = PaperTrader(portfolio=portfolio, repository=repository, risk_manager=RiskManager())

            result = trader.execute(signal="SELL", price=110.0, confidence=0.95, symbol="BTC/USDT")

            self.assertTrue(result.executed)
            self.assertEqual(result.signal, "SELL")
            self.assertIsNone(portfolio.position)
            self.assertIsNotNone(result.trade)

    def test_hold_is_ignored(self) -> None:
        portfolio = Portfolio()
        repository = Mock()
        trader = PaperTrader(portfolio=portfolio, repository=repository, risk_manager=RiskManager())

        result = trader.execute(signal="HOLD", price=100.0, confidence=0.95, symbol="BTC/USDT")

        self.assertFalse(result.executed)
        self.assertEqual(result.signal, "HOLD")
        repository.save_trade.assert_not_called()

    def test_repository_failure_is_handled(self) -> None:
        portfolio = Portfolio()
        repository = Mock()
        repository.save_trade.side_effect = RuntimeError("db failure")
        trader = PaperTrader(portfolio=portfolio, repository=repository, risk_manager=RiskManager())

        result = trader.execute(signal="BUY", price=100.0, confidence=0.95, symbol="BTC/USDT")

        self.assertFalse(result.executed)
        self.assertIsNone(result.trade)


if __name__ == "__main__":
    unittest.main()
