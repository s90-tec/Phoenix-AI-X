import time
import ccxt
import pandas as pd

from app.ai.predictor import predict_signal
from app.portfolio.portfolio import Portfolio

exchange = ccxt.binance()

portfolio = Portfolio()

print("=" * 60)
print("PHOENIX AI LIVE PAPER TRADER")
print("=" * 60)

while True:

    try:

        candles = exchange.fetch_ohlcv(
            "BTC/USDT",
            timeframe="1h",
            limit=100
        )

        df = pd.DataFrame(
            candles,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]
        )

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        latest_price = df.iloc[-1]["close"]

        signal, confidence = predict_signal(
            pd.read_csv("data/AI_Features.csv")
        )

        print("\n----------------------------------------")
        print("Time       :", df.iloc[-1]["timestamp"])
        print(f"Price      : ${latest_price:.2f}")
        print("Signal     :", signal)
        print(f"Confidence : {confidence:.2f}%")

        if signal == "BUY":
            portfolio.buy(latest_price)

        elif signal == "SELL":
            portfolio.sell(latest_price)

        print()

        print("Balance :", round(portfolio.balance, 2))
        print("Value   :", round(portfolio.value(latest_price), 2))
        print("Position:", portfolio.position)

        time.sleep(60)

    except Exception as e:
        print(e)
        time.sleep(10)