class Portfolio:

    def __init__(self):
        self.balance = 10000.0
        self.position = None
        self.entry_price = 0.0
        self.quantity = 0.0

    def buy(self, price):
        if self.position is None:
            self.quantity = self.balance / price
            self.entry_price = price
            self.position = "LONG"
            self.balance = 0.0
            print(f"BUY @ ${price:.2f}")

    def sell(self, price):
        if self.position == "LONG":
            self.balance = self.quantity * price
            self.quantity = 0.0
            self.position = None
            self.entry_price = 0.0
            print(f"SELL @ ${price:.2f}")

    def value(self, current_price):
        if self.position == "LONG":
            return self.quantity * current_price
        return self.balance