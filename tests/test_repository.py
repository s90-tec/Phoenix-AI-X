import os
import tempfile
import unittest

from app.database.database import create_database, save_trade
from app.database.repository import TradeRepository


class TradeRepositoryTests(unittest.TestCase):
    def test_repository_queries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "repo_trades.db")
            engine = create_database(db_path)
            repo = TradeRepository(engine)

            save_trade(
                engine=engine,
                timestamp="2026-07-18T10:00:00",
                symbol="BTC/USDT",
                side="BUY",
                price=100.0,
                quantity=1.0,
                confidence=0.9,
                pnl=10.0,
                balance=1010.0,
            )
            save_trade(
                engine=engine,
                timestamp="2026-07-18T11:00:00",
                symbol="BTC/USDT",
                side="SELL",
                price=110.0,
                quantity=1.0,
                confidence=0.8,
                pnl=10.0,
                balance=1110.0,
            )
            save_trade(
                engine=engine,
                timestamp="2026-07-18T12:00:00",
                symbol="ETH/USDT",
                side="BUY",
                price=200.0,
                quantity=2.0,
                confidence=0.8,
                pnl=-5.0,
                balance=2000.0,
            )

            all_trades = repo.get_all_trades()
            symbol_trades = repo.get_trades_by_symbol("BTC/USDT")
            recent_trades = repo.get_recent_trades(1)
            total_profit = repo.get_total_profit()
            win_rate = repo.get_win_rate()
            open_positions = repo.get_open_positions()

            self.assertEqual(len(all_trades), 3)
            self.assertEqual(len(symbol_trades), 2)
            self.assertEqual(len(recent_trades), 1)
            self.assertEqual(total_profit, 15.0)
            self.assertEqual(win_rate, 66.67)
            self.assertEqual(len(open_positions), 2)
            self.assertEqual({trade.symbol for trade in open_positions}, {"BTC/USDT", "ETH/USDT"})


if __name__ == "__main__":
    unittest.main()
