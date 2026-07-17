import pandas as pd
import ta

# Load historical data
df = pd.read_csv("data/BTC_USDT_1h.csv")

# EMA
df["EMA20"] = ta.trend.ema_indicator(df["close"], window=20)
df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)

# RSI
df["RSI"] = ta.momentum.rsi(df["close"], window=14)

# MACD
macd = ta.trend.MACD(df["close"])

df["MACD"] = macd.macd()
df["Signal"] = macd.macd_signal()

# Bollinger Bands
bb = ta.volatility.BollingerBands(df["close"])

df["Upper Band"] = bb.bollinger_hband()
df["Lower Band"] = bb.bollinger_lband()

# Save the enriched data
df.to_csv("data/BTC_USDT_Indicators.csv", index=False)

print("=" * 60)
print("Phoenix AI Trader - Indicator Engine")
print("=" * 60)

print(df.tail())

print("\nIndicators saved to:")
print("data/BTC_USDT_Indicators.csv")