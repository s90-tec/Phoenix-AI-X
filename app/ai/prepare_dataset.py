import pandas as pd
import os

INPUT = "data/BTC_USDT_Indicators.csv"

OUTPUT = "data/AI_Dataset.csv"

if not os.path.exists(INPUT):
    print("Indicator file not found!")
    exit()

df = pd.read_csv(INPUT)

# Target:
# 1 = Next candle closes higher
# 0 = Next candle closes lower

df["Target"] = (
    df["close"].shift(-1) > df["close"]
).astype(int)

# Remove last row
df = df[:-1]

features = [
    "RSI",
    "EMA20",
    "EMA50",
    "MACD",
    "Signal",
    "volume",
]

dataset = df[features + ["Target"]]

dataset.to_csv(OUTPUT, index=False)

print("=" * 60)
print("Phoenix AI Trader")
print("=" * 60)

print(dataset.tail())

print()

print("Dataset Saved")

print(OUTPUT)