class Portfolio:

    def __init__(self, capital=10000):

        self.cash = capital
        self.coin = 0

        self.position = False

        self.initial = capital

    def buy(self, price):

        if not self.position:

            self.coin = self.cash / price

            self.cash = 0

            self.position = True

    def sell(self, price):

        if self.position:

            self.cash = self.coin * price

            self.coin = 0

            self.position = False

    def value(self, current_price):

        if self.position:

            return self.coin * current_price

        return self.cash