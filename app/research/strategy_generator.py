"""Candidate strategy generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StrategyCandidate:
    name: str
    indicators: list[str]
    filters: list[str]
    entry_rule: str
    exit_rule: str
    risk_rules: dict[str, Any] = field(default_factory=dict)


class StrategyGenerator:
    """Composes registered indicators, rules, and risk controls into strategies."""

    def __init__(self) -> None:
        self._strategies: dict[str, StrategyCandidate] = {}

    def generate(self) -> list[StrategyCandidate]:
        candidates = [
            StrategyCandidate("trend_volatility_breakout", ["EMA_spread", "ATR_expansion"], ["market_regime"], "EMA spread is positive and ATR expands", "EMA spread reverses", {"stop_atr": 2.0, "risk_per_trade": 0.01}),
            StrategyCandidate("rsi_adx_trend_entry", ["RSI_momentum", "ADX"], ["market_regime"], "RSI rises above threshold while ADX confirms", "RSI momentum turns negative", {"stop_atr": 1.5, "risk_per_trade": 0.01}),
            StrategyCandidate("vwap_volume_reversion", ["VWAP_deviation", "volume_imbalance"], ["volatility_cluster"], "Extreme VWAP deviation with volume confirmation", "Price returns to VWAP", {"stop_atr": 1.2, "risk_per_trade": 0.005}),
        ]
        for candidate in candidates:
            self._strategies.setdefault(candidate.name, candidate)
        return self.strategies()

    def strategies(self) -> list[StrategyCandidate]:
        return list(self._strategies.values())
