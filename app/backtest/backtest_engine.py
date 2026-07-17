import pandas as pd

from portfolio import Portfolio

from metrics import *

data = pd.read_csv("data/BTC_USDT_Strategy.csv")

portfolio = Portfolio(10000)

wins = 0
loss = 0

trades = []

buy_price = 0

for i in range(len(data)):

    signal = data.loc[i, "TradeSignal"]

    price = data.loc[i, "close"]

    time = data.loc[i, "timestamp"]

    if signal == "BUY":

        if not portfolio.position:

            portfolio.buy(price)

            buy_price = price

            trades.append(("BUY", time, price))

    elif signal == "SELL":

        if portfolio.position:

            portfolio.sell(price)

            trades.append(("SELL", time, price))

            if price > buy_price:

                wins += 1

            else:

                loss += 1

final_balance = portfolio.value(data.iloc[-1]["close"])

print("=" * 70)

print("PHOENIX AI TRADER PRO")

print("=" * 70)

print(f"Initial Balance : ${portfolio.initial:,.2f}")

print(f"Final Balance   : ${final_balance:,.2f}")

print(f"Profit          : ${profit(portfolio.initial, final_balance):,.2f}")

print(f"ROI             : {roi(portfolio.initial, final_balance):.2f}%")

print()

print(f"Winning Trades  : {wins}")

print(f"Losing Trades   : {loss}")

print(f"Win Rate        : {win_rate(wins, wins+loss):.2f}%")

print()

print("Trade History")

for trade in trades:

    print(trade)