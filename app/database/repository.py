from __future__ import annotations

from typing import List

from sqlalchemy import func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.database.database import Trade, save_trade


class TradeRepository:
    """Repository for reading trade records from the SQLite database."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def _session(self) -> Session:
        return Session(self.engine)

    def get_all_trades(self) -> List[Trade]:
        with self._session() as session:
            return list(session.query(Trade).order_by(Trade.id.asc()).all())

    def get_trades_by_symbol(self, symbol: str) -> List[Trade]:
        with self._session() as session:
            return list(
                session.query(Trade)
                .filter(Trade.symbol == symbol)
                .order_by(Trade.id.asc())
                .all()
            )

    def get_recent_trades(self, limit: int) -> List[Trade]:
        with self._session() as session:
            return list(
                session.query(Trade)
                .order_by(Trade.id.desc())
                .limit(limit)
                .all()
            )

    def get_total_profit(self) -> float:
        with self._session() as session:
            result = session.query(func.coalesce(func.sum(Trade.pnl), 0.0)).scalar()
            return float(result or 0.0)

    def get_win_rate(self) -> float:
        with self._session() as session:
            total = session.query(Trade).count()
            if total == 0:
                return 0.0
            profitable = (
                session.query(Trade)
                .filter(Trade.pnl.is_not(None))
                .filter(Trade.pnl > 0)
                .count()
            )
            return round((profitable / total) * 100.0, 2)

    def get_open_positions(self) -> List[Trade]:
        with self._session() as session:
            trades = (
                session.query(Trade)
                .filter(Trade.side.in_(["BUY", "SELL"]))
                .order_by(Trade.id.asc())
                .all()
            )

            open_entries: List[Trade] = []
            open_symbols: set[str] = set()

            for trade in trades:
                if trade.side == "BUY" and trade.symbol not in open_symbols:
                    open_entries.append(trade)
                    open_symbols.add(trade.symbol)
                elif trade.side == "SELL" and trade.symbol in open_symbols:
                    open_symbols.remove(trade.symbol)

            return open_entries

    def save_trade(
        self,
        timestamp: str,
        symbol: str,
        side: str,
        price: float,
        quantity: float,
        confidence: float | None = None,
        pnl: float | None = None,
        balance: float | None = None,
    ) -> Trade:
        """Persist a trade via the existing database save_trade function."""
        return save_trade(
            engine=self.engine,
            timestamp=timestamp,
            symbol=symbol,
            side=side,
            price=price,
            quantity=quantity,
            confidence=confidence,
            pnl=pnl,
            balance=balance,
        )
