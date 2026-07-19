from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from app.database.database import Trade
from app.database.repository import TradeRepository
from app.portfolio.portfolio import Portfolio
from app.risk.risk_manager import RiskManager

logger = logging.getLogger(__name__)


@dataclass
class TradeResult:
    """Structured result returned after attempting an execution."""

    signal: str
    executed: bool
    price: float
    quantity: float
    balance: float
    pnl: float
    trade: Optional[Trade] = None


class PaperTrader:
    """Execute paper-trading actions while keeping execution concerns separate."""

    def __init__(
        self,
        portfolio: Portfolio,
        repository: TradeRepository,
        risk_manager: Optional[RiskManager] = None,
        logger_instance: Optional[logging.Logger] = None,
    ) -> None:
        self.portfolio = portfolio
        self.repository = repository
        self.risk_manager = risk_manager or RiskManager()
        self.logger = logger_instance or logger

    def execute(self, signal: str, price: float, confidence: float, symbol: str) -> TradeResult:
        """Execute a BUY/SELL/HOLD signal and persist the trade if needed."""
        if signal == "HOLD":
            self.logger.info("Ignoring HOLD signal")
            return TradeResult(signal=signal, executed=False, price=price, quantity=0.0, balance=self.portfolio.balance, pnl=0.0)

        try:
            signal = self.risk_manager.manage_risk(signal, confidence, price)
        except Exception as exc:  # pragma: no cover - defensive runtime path
            self.logger.exception("Risk manager failed: %s", exc)
            signal = "HOLD"

        if signal == "HOLD":
            self.logger.info("Signal converted to HOLD by risk manager")
            return TradeResult(signal=signal, executed=False, price=price, quantity=0.0, balance=self.portfolio.balance, pnl=0.0)

        if signal == "BUY":
            return self.buy(price=price, confidence=confidence, symbol=symbol)
        if signal == "SELL":
            return self.sell(price=price, confidence=confidence, symbol=symbol)

        self.logger.warning("Unsupported signal received: %s", signal)
        return TradeResult(signal=signal, executed=False, price=price, quantity=0.0, balance=self.portfolio.balance, pnl=0.0)

    def buy(self, price: float, confidence: float, symbol: str) -> TradeResult:
        """Execute a BUY order and persist it."""
        try:
            self.portfolio.buy(price)
            quantity = self.portfolio.quantity
            balance = self.portfolio.balance
            trade = self._persist_trade(
                side="BUY",
                price=price,
                quantity=quantity,
                confidence=confidence,
                symbol=symbol,
                balance=balance,
                pnl=0.0,
            )
            executed = trade is not None
            self.logger.info("BUY executed successfully")
            return TradeResult(
                signal="BUY",
                executed=executed,
                price=price,
                quantity=quantity,
                balance=balance,
                pnl=0.0,
                trade=trade,
            )
        except Exception as exc:  # pragma: no cover - defensive runtime path
            self.logger.exception("BUY execution failed: %s", exc)
            return TradeResult(signal="BUY", executed=False, price=price, quantity=0.0, balance=self.portfolio.balance, pnl=0.0)

    def sell(self, price: float, confidence: float, symbol: str) -> TradeResult:
        """Execute a SELL order and persist it."""
        try:
            entry_price = self.portfolio.entry_price
            quantity = self.portfolio.quantity
            pnl = 0.0
            if quantity > 0 and entry_price > 0:
                pnl = (price - entry_price) * quantity

            self.portfolio.sell(price)
            balance = self.portfolio.balance
            trade = self._persist_trade(
                side="SELL",
                price=price,
                quantity=quantity,
                confidence=confidence,
                symbol=symbol,
                balance=balance,
                pnl=pnl,
            )
            executed = trade is not None
            self.logger.info("SELL executed successfully")
            return TradeResult(
                signal="SELL",
                executed=executed,
                price=price,
                quantity=quantity,
                balance=balance,
                pnl=pnl,
                trade=trade,
            )
        except Exception as exc:  # pragma: no cover - defensive runtime path
            self.logger.exception("SELL execution failed: %s", exc)
            return TradeResult(signal="SELL", executed=False, price=price, quantity=0.0, balance=self.portfolio.balance, pnl=0.0)

    def _persist_trade(
        self,
        side: str,
        price: float,
        quantity: float,
        confidence: float,
        symbol: str,
        balance: float,
        pnl: float,
    ) -> Optional[Trade]:
        """Persist the executed trade using the repository."""
        try:
            trade = self.repository.save_trade(
                timestamp="",
                symbol=symbol,
                side=side,
                price=price,
                quantity=quantity,
                confidence=confidence,
                pnl=pnl,
                balance=balance,
            )
            self.logger.info("Trade saved successfully")
            return trade
        except Exception as exc:  # pragma: no cover - defensive runtime path
            self.logger.exception("Failed to save trade: %s", exc)
            return None
