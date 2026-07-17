import ccxt
import pandas as pd
import os

exchange = ccxt.binance()

symbol = "BTC/USDT"
timeframe = "1h"
limit = 1000

print("Downloading data...")

ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

df = pd.DataFrame(
    ohlcv,
    columns=[
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ],
)

df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

os.makedirs("data", exist_ok=True)

filename = "data/BTC_USDT_1h.csv"

df.to_csv(filename, index=False)

print(f"Downloaded {len(df)} candles")
print(f"Saved to {filename}")

print("\nLast 5 candles:\n")
print(df.tail())
