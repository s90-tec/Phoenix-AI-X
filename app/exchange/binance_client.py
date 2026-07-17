import ccxt
import time
from datetime import datetime

exchange = ccxt.binance()

print("=" * 50)
print("🚀 Phoenix AI Trader - Live Monitor")
print("=" * 50)

while True:
    try:
        ticker = exchange.fetch_ticker("BTC/USDT")

        price = ticker["last"]

        print(
            f"{datetime.now().strftime('%H:%M:%S')} | BTC/USDT : ${price:,.2f}"
        )

        time.sleep(5)

    except Exception as e:
        print("Error:", e)
        time.sleep(5)