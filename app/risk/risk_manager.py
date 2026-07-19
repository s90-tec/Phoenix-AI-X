from __future__ import annotations

import logging
from typing import Any, Optional

from app.config import config
from app.portfolio.portfolio import Portfolio

logger = logging.getLogger(__name__)


class RiskManager:
    """Risk gate for paper-trading decisions using configurable thresholds."""

    def __init__(
        self,
        config_module: Optional[Any] = None,
        portfolio: Optional[Portfolio] = None,
        logger_instance: Optional[logging.Logger] = None,
    ) -> None:
        self.config_module = config_module or config
        self.portfolio = portfolio or Portfolio()
        self.logger = logger_instance or logger
        self._daily_trade_count = 0
        self._daily_loss = 0.0
        self._starting_balance = float(self.portfolio.balance)
        self._max_drawdown = 0.0
        self._daily_trade_results: list[dict[str, Any]] = []

    def can_execute(self, signal: str, confidence: float, symbol: str, price: float) -> bool:
        """Return True when the signal passes all configured risk rules."""
        if signal not in {"BUY", "SELL"}:
            self._reject("unsupported signal", signal=symbol)
            return False

        if confidence < self.config_module.MIN_CONFIDENCE:
            self._reject("confidence below threshold", symbol=symbol, confidence=confidence)
            return False

        if self.portfolio.position is not None and signal == "BUY":
            self._reject("position already open", symbol=symbol)
            return False

        if self._daily_trade_count >= self.config_module.MAX_TRADES_PER_DAY:
            self._reject("maximum trades per day exceeded", symbol=symbol)
            return False

        if self._daily_loss <= -abs(self.config_module.DAILY_LOSS_LIMIT):
            self._reject("daily loss exceeded", symbol=symbol, daily_loss=self._daily_loss)
            return False

        if self._max_drawdown >= self.config_module.MAX_DRAWDOWN:
            self._reject("drawdown exceeded", symbol=symbol, drawdown=self._max_drawdown)
            return False

        max_risk_per_trade = self.config_module.MAX_RISK_PER_TRADE
        if max_risk_per_trade <= 0:
            self._reject("max risk per trade invalid", symbol=symbol)
            return False

        position_size = self.calculate_position_size(
            balance=self.portfolio.balance,
            risk_percent=max_risk_per_trade,
            stop_loss_distance=self.config_module.STOP_LOSS_PERCENTAGE,
        )
        if position_size <= 0:
            self._reject("position size invalid", symbol=symbol)
            return False

        if position_size > self.config_module.MAX_POSITION_SIZE:
            self._reject("position size exceeds maximum", symbol=symbol, position_size=position_size)
            return False

        return True

    def calculate_position_size(self, balance: float, risk_percent: float, stop_loss_distance: float) -> float:
        """Calculate a position size based on balance, risk, and stop-loss distance."""
        if balance <= 0 or risk_percent <= 0 or stop_loss_distance <= 0:
            return 0.0
        risk_amount = balance * risk_percent
        return risk_amount / stop_loss_distance

    def should_exit(self, position: dict[str, Any], current_price: float) -> bool:
        """Return True when the current price triggers stop-loss or take-profit."""
        entry_price = float(position.get("entry_price", 0.0))
        if entry_price <= 0:
            return False

        stop_loss_distance = self.config_module.STOP_LOSS_PERCENTAGE
        take_profit_distance = self.config_module.TAKE_PROFIT_PERCENTAGE

        stop_loss_price = entry_price * (1 - stop_loss_distance)
        take_profit_price = entry_price * (1 + take_profit_distance)

        if current_price <= stop_loss_price:
            return True
        if current_price >= take_profit_price:
            return True
        return False

    def record_trade_result(
        self,
        signal: str,
        executed: bool,
        price: float,
        quantity: float,
        balance: float,
        pnl: float,
    ) -> None:
        """Update daily counters and drawdown state from the latest trade result."""
        self._daily_trade_count += 1
        self._daily_loss += pnl
        if self._starting_balance > 0:
            drawdown = max(0.0, (self._starting_balance - balance) / self._starting_balance)
            self._max_drawdown = max(self._max_drawdown, drawdown)
        self._daily_trade_results.append(
            {
                "signal": signal,
                "executed": executed,
                "price": price,
                "quantity": quantity,
                "balance": balance,
                "pnl": pnl,
            }
        )

    def manage_risk(self, signal: str, confidence: float, price: float) -> str:
        """Backward-compatible wrapper used by the paper trader."""
        if not self.can_execute(signal, confidence, "", price):
            return "HOLD"
        return signal

    def _reject(self, reason: str, **details: Any) -> None:
        details_str = ", ".join(f"{k}={v}" for k, v in sorted(details.items()))
        self.logger.info("Rejected trade: %s%s", reason, f" ({details_str})" if details_str else "")
