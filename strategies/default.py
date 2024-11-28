from cointrader.common.Strategy import Strategy
from cointrader.indicators.MACD import MACD

class Default(Strategy):
    def __init__(self):
        super().__init__('default')
        self.macd = MACD('macd')

    def update(self, kline):
        self.macd.update(kline)

    def buy(self):
        pass

    def sell(self):
        pass
