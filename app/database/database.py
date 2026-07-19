from __future__ import annotations

from typing import Optional

from sqlalchemy import Float, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    side: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pnl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    balance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


def create_database(db_path: str = "phoenix_trades.db"):
    """Create a SQLite database engine and initialize the schema."""
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine


def save_trade(
    engine,
    timestamp: str,
    symbol: str,
    side: str,
    price: float,
    quantity: float,
    confidence: Optional[float] = None,
    pnl: Optional[float] = None,
    balance: Optional[float] = None,
) -> Trade:
    """Persist a trade record to the database and return it."""
    with Session(engine) as session:
        trade = Trade(
            timestamp=timestamp,
            symbol=symbol,
            side=side,
            price=price,
            quantity=quantity,
            confidence=confidence,
            pnl=pnl,
            balance=balance,
        )
        session.add(trade)
        session.commit()
        session.refresh(trade)
        return trade
