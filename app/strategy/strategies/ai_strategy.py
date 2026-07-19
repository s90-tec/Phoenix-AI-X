from __future__ import annotations

import pandas as pd

from app.ai.predictor import Predictor
from app.strategy.base import BaseStrategy, Signal


class AIStrategy(BaseStrategy):
    """Adapt the existing predictor into the new strategy framework."""

    name = "ai_strategy"

    def __init__(self, predictor: Predictor | None = None) -> None:
        self.predictor = predictor or Predictor()

    def generate_signal(self, features: pd.DataFrame) -> Signal:
        try:
            signal, confidence = self.predictor.predict_signal(features)
        except Exception as exc:  # pragma: no cover - defensive execution path
            return Signal(strategy_name=self.name, symbol="", signal="HOLD", confidence=0.0, timestamp="", reason=f"Prediction failed: {exc}", metadata={})
        return Signal(strategy_name=self.name, symbol="", signal=signal, confidence=float(confidence), timestamp="", reason="AI model prediction", metadata={})
