from backtesting import Strategy
from backtesting.lib import crossover
from backtesting.test import SMA


class SmaCross (Strategy):
    ns = 5   # Short
    nl = 25  # Long

    def init(self):
        # Short average
        self.smaS = self.I(SMA, self.data["Close"], self.ns)
        # Long average
        self.smaL = self.I(SMA, self.data["Close"], self.nl)
        return

    def next(self):
        # Buy on  smaS > smaL
        if crossover(self.smaS, self.smaL):
            self.buy()

        # Sell on smaS < smaL
        elif crossover(self.smaL, self.smaS):
            self.position.close()
        return



    
