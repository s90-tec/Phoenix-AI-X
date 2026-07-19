from __future__ import annotations

import pandas as pd

from app.strategy.base import BaseStrategy, Signal


class GridStrategy(BaseStrategy):
    """A placeholder grid strategy that stays neutral unless configured otherwise."""

    name = "grid"

    def generate_signal(self, features: pd.DataFrame) -> Signal:
        return Signal(strategy_name=self.name, symbol="", signal="HOLD", confidence=0.1, timestamp="", reason="Grid strategy placeholder", metadata={})
