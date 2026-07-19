import os
import tempfile
import unittest

from app.database.database import create_database, save_trade


class DatabaseModuleTests(unittest.TestCase):
    def test_create_database_and_save_trade(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_trades.db")
            engine = create_database(db_path)
            self.assertIsNotNone(engine)

            trade = save_trade(
                engine=engine,
                timestamp="2026-07-18T12:00:00",
                symbol="BTC/USDT",
                side="buy",
                price=50000.0,
                quantity=0.01,
                confidence=0.92,
                pnl=0.0,
                balance=50000.0,
            )

            self.assertIsNotNone(trade.id)
            self.assertEqual(trade.symbol, "BTC/USDT")
            self.assertEqual(trade.side, "buy")


if __name__ == "__main__":
    unittest.main()
