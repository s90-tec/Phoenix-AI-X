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

model = joblib.load(MODEL)


def predict_signal(df):
    latest = df.iloc[-1]

    X = pd.DataFrame([latest[FEATURES]])

    prediction = model.predict(X)[0]

    probability = model.predict_proba(X)[0]

    confidence = probability.max() * 100

    labels = {
        0: "SELL",
        1: "HOLD",
        2: "BUY",
    }

    return labels[prediction], confidence