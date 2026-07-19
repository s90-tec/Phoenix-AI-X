"""Candidate feature discovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FeatureCandidate:
    name: str
    description: str
    category: str
    parameters: dict[str, Any] = field(default_factory=dict)


class FeatureDiscovery:
    """Produces and retains reusable, deterministic market features."""

    def __init__(self) -> None:
        self._features: dict[str, FeatureCandidate] = {}

    def discover(self) -> list[FeatureCandidate]:
        candidates = [
            FeatureCandidate("EMA_spread", "Fast EMA minus slow EMA", "trend", {"fast": 12, "slow": 26}),
            FeatureCandidate("RSI_momentum", "Change in RSI over a lookback", "momentum", {"period": 14, "lookback": 3}),
            FeatureCandidate("ATR_expansion", "ATR relative to its moving average", "volatility", {"period": 14}),
            FeatureCandidate("VWAP_deviation", "Price distance from VWAP", "mean_reversion"),
            FeatureCandidate("volume_imbalance", "Buy versus sell volume imbalance", "volume"),
            FeatureCandidate("volatility_cluster", "Discrete rolling-volatility regime", "regime"),
            FeatureCandidate("market_regime", "Encoded trend and volatility regime", "regime"),
        ]
        for candidate in candidates:
            self._features.setdefault(candidate.name, candidate)
        return self.features()

    def features(self) -> list[FeatureCandidate]:
        return list(self._features.values())
