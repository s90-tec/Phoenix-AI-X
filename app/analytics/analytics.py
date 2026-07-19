from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.database.repository import TradeRepository


class AnalyticsEngine:
    """Read-only performance analytics over completed trades from a repository."""

    def __init__(self, repository: TradeRepository) -> None:
        self.repository = repository

    def _trades_frame(self) -> pd.DataFrame:
        trades = self.repository.get_all_trades()
        if not trades:
            return pd.DataFrame(columns=["id", "timestamp", "symbol", "side", "price", "quantity", "confidence", "pnl", "balance"])

        frame = pd.DataFrame(
            [
                {
                    "id": trade.id,
                    "timestamp": trade.timestamp,
                    "symbol": trade.symbol,
                    "side": trade.side,
                    "price": float(trade.price),
                    "quantity": float(trade.quantity),
                    "confidence": float(trade.confidence) if trade.confidence is not None else np.nan,
                    "pnl": float(trade.pnl) if trade.pnl is not None else np.nan,
                    "balance": float(trade.balance) if trade.balance is not None else np.nan,
                }
                for trade in trades
            ]
        )
        frame = frame.sort_values("id").reset_index(drop=True)
        frame["pnl"] = pd.to_numeric(frame["pnl"], errors="coerce")
        frame["balance"] = pd.to_numeric(frame["balance"], errors="coerce")
        return frame

    def _equity_curve(self, trades: pd.DataFrame) -> pd.Series:
        if trades.empty:
            return pd.Series(dtype=float)
        cumulative = trades["pnl"].fillna(0.0).cumsum()
        return cumulative

    def get_total_return(self) -> float:
        trades = self._trades_frame()
        if trades.empty:
            return 0.0
        initial_balance = float(trades.iloc[0]["balance"] or 0.0)
        if initial_balance <= 0:
            return 0.0
        final_balance = float(trades.iloc[-1]["balance"] or 0.0)
        return round(((final_balance / initial_balance) - 1.0) * 100.0, 2)

    def get_total_pnl(self) -> float:
        trades = self._trades_frame()
        return round(float(trades["pnl"].sum()), 2) if not trades.empty else 0.0

    def get_win_rate(self) -> float:
        trades = self._trades_frame()
        if trades.empty:
            return 0.0
        winners = int((trades["pnl"] > 0).sum())
        return round((winners / len(trades)) * 100.0, 2)

    def get_profit_factor(self) -> float:
        trades = self._trades_frame()
        if trades.empty:
            return 0.0
        gross_profit = float(trades.loc[trades["pnl"] > 0, "pnl"].sum())
        gross_loss = abs(float(trades.loc[trades["pnl"] < 0, "pnl"].sum()))
        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0
        return round(gross_profit / gross_loss, 2)

    def get_average_win(self) -> float:
        trades = self._trades_frame()
        wins = trades.loc[trades["pnl"] > 0, "pnl"]
        if wins.empty:
            return 0.0
        return round(float(wins.mean()), 2)

    def get_average_loss(self) -> float:
        trades = self._trades_frame()
        losses = trades.loc[trades["pnl"] < 0, "pnl"]
        if losses.empty:
            return 0.0
        return round(float(losses.mean()), 2)

    def get_max_drawdown(self) -> float:
        trades = self._trades_frame()
        if trades.empty:
            return 0.0
        equity = self._equity_curve(trades)
        if equity.empty:
            return 0.0
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max.replace(0, np.nan)
        return round(float(drawdown.min() * 100.0), 2) if not drawdown.empty else 0.0

    def get_sharpe_ratio(self) -> float:
        trades = self._trades_frame()
        if trades.empty:
            return 0.0
        pnl_series = trades["pnl"].fillna(0.0)
        if pnl_series.std() == 0:
            return 0.0
        return round(float(pnl_series.mean() / pnl_series.std()), 2)

    def get_trade_count(self) -> int:
        trades = self._trades_frame()
        return int(len(trades))

    def get_average_trade_duration(self) -> float:
        return 0.0

    def get_daily_pnl(self) -> pd.DataFrame:
        trades = self._trades_frame()
        if trades.empty:
            return pd.DataFrame(columns=["date", "pnl"])
        trades = trades.copy()
        trades["date"] = pd.to_datetime(trades["timestamp"], errors="coerce").dt.date
        return trades.groupby("date")["pnl"].sum().reset_index(name="pnl")

    def get_weekly_pnl(self) -> pd.DataFrame:
        trades = self._trades_frame()
        if trades.empty:
            return pd.DataFrame(columns=["week", "pnl"])
        trades = trades.copy()
        trades["date"] = pd.to_datetime(trades["timestamp"], errors="coerce")
        trades["week"] = trades["date"].dt.to_period("W-MON").astype(str)
        return trades.groupby("week")["pnl"].sum().reset_index(name="pnl")

    def get_monthly_pnl(self) -> pd.DataFrame:
        trades = self._trades_frame()
        if trades.empty:
            return pd.DataFrame(columns=["month", "pnl"])
        trades = trades.copy()
        trades["date"] = pd.to_datetime(trades["timestamp"], errors="coerce")
        trades["month"] = trades["date"].dt.to_period("M").astype(str)
        return trades.groupby("month")["pnl"].sum().reset_index(name="pnl")

    def generate_summary(self) -> dict[str, Any]:
        return {
            "total_return": self.get_total_return(),
            "win_rate": self.get_win_rate(),
            "profit_factor": self.get_profit_factor(),
            "drawdown": self.get_max_drawdown(),
            "trade_count": self.get_trade_count(),
        }
