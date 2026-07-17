import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import joblib
import os

st.set_page_config(
    page_title="Phoenix AI Trader",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Phoenix AI Trader v3.0")

# -----------------------
# Load Data
# -----------------------

DATA = "data/BTC_USDT_Strategy.csv"

MODEL = "models/xgboost_model.pkl"

if not os.path.exists(DATA):
    st.error("Strategy data not found.")
    st.stop()

df = pd.read_csv(DATA)

latest = df.iloc[-1]

# -----------------------
# AI Prediction
# -----------------------

prediction = "N/A"
confidence = "N/A"

if os.path.exists(MODEL):

    model = joblib.load(MODEL)

    features = latest[
        [
            "RSI",
            "EMA20",
            "EMA50",
            "MACD",
            "Signal",
            "volume",
        ]
    ]

    probability = model.predict_proba([features])[0]

    confidence = round(max(probability) * 100, 2)

    if probability[1] > 0.5:
        prediction = "BUY"
    else:
        prediction = "SELL"

# -----------------------
# Top Cards
# -----------------------

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "BTC Price",
        f"${latest['close']:,.2f}"
    )

with c2:
    st.metric(
        "Strategy",
        latest["TradeSignal"]
    )

with c3:
    st.metric(
        "AI Prediction",
        prediction
    )

with c4:
    st.metric(
        "Confidence",
        f"{confidence}%"
    )

# -----------------------
# Candlestick Chart
# -----------------------

st.subheader("BTC Candlestick Chart")

fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="BTC"
    )
)

fig.update_layout(
    height=600,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------
# EMA Chart
# -----------------------

st.subheader("EMA20 vs EMA50")

ema = go.Figure()

ema.add_trace(
    go.Scatter(
        x=df["timestamp"],
        y=df["EMA20"],
        name="EMA20"
    )
)

ema.add_trace(
    go.Scatter(
        x=df["timestamp"],
        y=df["EMA50"],
        name="EMA50"
    )
)

st.plotly_chart(
    ema,
    use_container_width=True
)

# -----------------------
# Indicators
# -----------------------

st.subheader("Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "RSI",
        round(latest["RSI"],2)
    )

with col2:
    st.metric(
        "MACD",
        round(latest["MACD"],2)
    )

with col3:
    st.metric(
        "Volume",
        round(latest["volume"],2)
    )

# -----------------------
# Signals
# -----------------------

st.subheader("Trade Signals")

signals = df[df["TradeSignal"] != "HOLD"]

st.dataframe(
    signals.tail(20),
    width="stretch"
)