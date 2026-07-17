import pandas as pd
import numpy as np
import ta
import os

INPUT = "data/BTC_USDT_1h.csv"
OUTPUT = "data/AI_Features.csv"

if not os.path.exists(INPUT):
    print("Market data not found!")
    exit()

df = pd.read_csv(INPUT)

# ===========================
# Trend Indicators
# ===========================

df["EMA20"] = ta.trend.ema_indicator(df["close"], window=20)
df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)
df["EMA100"] = ta.trend.ema_indicator(df["close"], window=100)
df["EMA200"] = ta.trend.ema_indicator(df["close"], window=200)

# ===========================
# Momentum
# ===========================

df["RSI"] = ta.momentum.rsi(df["close"], window=14)

macd = ta.trend.MACD(df["close"])

df["MACD"] = macd.macd()
df["MACD_Signal"] = macd.macd_signal()
df["MACD_Hist"] = macd.macd_diff()

# ===========================
# Volatility
# ===========================

bb = ta.volatility.BollingerBands(df["close"])

df["BB_Upper"] = bb.bollinger_hband()
df["BB_Lower"] = bb.bollinger_lband()
df["BB_Width"] = bb.bollinger_wband()

# ===========================
# ATR
# ===========================

df["ATR"] = ta.volatility.average_true_range(
    df["high"],
    df["low"],
    df["close"]
)

# ===========================
# ADX
# ===========================

df["ADX"] = ta.trend.adx(
    df["high"],
    df["low"],
    df["close"]
)

# ===========================
# Returns
# ===========================

df["Return1"] = df["close"].pct_change(1)
df["Return5"] = df["close"].pct_change(5)

# ===========================
# Volume
# ===========================

df["Volume_MA"] = df["volume"].rolling(20).mean()

# ===========================
# Better Target
# ===========================

future = df["close"].shift(-5)

gain = (future - df["close"]) / df["close"]

def create_target(x):
    if x > 0.005:
        return 2      # BUY
    elif x < -0.005:
        return 0      # SELL
    else:
        return 1      # HOLD

df["Target"] = gain.apply(create_target)

df.dropna(inplace=True)

df.to_csv(OUTPUT, index=False)

print("=" * 60)
print("Phoenix AI Feature Engineering")
print("=" * 60)

print(df.tail())

print("\nSaved")

print(OUTPUT)