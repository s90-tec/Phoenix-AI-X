import pandas as pd
from app.ai.predictor import predict_signal
from app.portfolio.portfolio import Portfolio

print("=" * 60)
print("PHOENIX AI PAPER TRADER")
print("=" * 60)

portfolio = Portfolio()

df = pd.read_csv("data/AI_Features.csv")

signal, confidence = predict_signal(df)

price = df.iloc[-1]["close"]

print(f"Current Price : ${price:.2f}")
print(f"AI Signal     : {signal}")
print(f"Confidence    : {confidence:.2f}%")
print()

if signal == "BUY":
    portfolio.buy(price)

elif signal == "SELL":
    portfolio.sell(price)

print()
print("=" * 60)
print("Portfolio")
print("=" * 60)
print(f"Balance : ${portfolio.balance:.2f}")
print(f"Value   : ${portfolio.value(price):.2f}")
print(f"Position: {portfolio.position}")