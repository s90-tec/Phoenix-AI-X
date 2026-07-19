import logging
from typing import Tuple

import joblib
import pandas as pd

MODEL = "models/xgboost_v2.pkl"

FEATURES = [
    "EMA20",
    "EMA50",
    "EMA100",
    "EMA200",
    "RSI",
    "MACD",
    "MACD_Signal",
    "MACD_Hist",
    "ATR",
    "ADX",
    "Return1",
    "Return5",
    "Volume_MA",
]

logger = logging.getLogger(__name__)


class Predictor:
    """Predict BUY/HOLD/SELL signals from a single-row feature DataFrame."""

    def __init__(self, model_path: str = MODEL) -> None:
        self.model_path = model_path
        self.model = joblib.load(model_path)

    def predict_signal(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Predict a signal from a single-row feature DataFrame."""
        if df.empty:
            raise ValueError("Feature dataframe is empty")

        latest = df.iloc[-1]
        missing_features = [feature for feature in FEATURES if feature not in latest.index]
        if missing_features:
            raise ValueError(f"Missing expected features: {missing_features}")

        X = pd.DataFrame([latest[FEATURES]])

        try:
            prediction = self.model.predict(X)[0]
            probability = self.model.predict_proba(X)[0]
            confidence = probability.max() * 100
        except Exception as exc:  # pragma: no cover - runtime robustness
            logger.exception("Prediction failed: %s", exc)
            raise

        labels = {
            0: "SELL",
            1: "HOLD",
            2: "BUY",
        }

        return labels[prediction], confidence


def predict_signal(df: pd.DataFrame) -> Tuple[str, float]:
    """Backward-compatible helper for existing callers."""
    return Predictor().predict_signal(df)