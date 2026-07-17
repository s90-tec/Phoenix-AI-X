import pandas as pd
import os

FILE = "data/BTC_USDT_Indicators.csv"

if not os.path.exists(FILE):
    print("Indicator file not found!")
    exit()

df = pd.read_csv(FILE)

# Default signal
df["TradeSignal"] = "HOLD"

# Generate signals using indicator crossovers
for i in range(1, len(df)):

    # Buy: EMA20 crosses above EMA50 AND MACD crosses above Signal
    if (
        df.loc[i - 1, "EMA20"] <= df.loc[i - 1, "EMA50"]
        and df.loc[i, "EMA20"] > df.loc[i, "EMA50"]
        and df.loc[i, "MACD"] > df.loc[i, "Signal"]
    ):
        df.loc[i, "TradeSignal"] = "BUY"

    # Sell: EMA20 crosses below EMA50 AND MACD crosses below Signal
    elif (
        df.loc[i - 1, "EMA20"] >= df.loc[i - 1, "EMA50"]
        and df.loc[i, "EMA20"] < df.loc[i, "EMA50"]
        and df.loc[i, "MACD"] < df.loc[i, "Signal"]
    ):
        df.loc[i, "TradeSignal"] = "SELL"

# Save results
output = "data/BTC_USDT_Strategy.csv"
df.to_csv(output, index=False)

print("=" * 70)
print("Phoenix AI Trader - Strategy Engine")
print("=" * 70)

print(df[[
    "timestamp",
    "close",
    "EMA20",
    "EMA50",
    "MACD",
    "Signal",
    "TradeSignal"
]].tail(30))

print("\nTrade Signal Count")
print(df["TradeSignal"].value_counts())

print("\nSaved:", output)