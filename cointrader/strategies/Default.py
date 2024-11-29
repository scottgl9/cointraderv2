from cointrader.common.Strategy import Strategy
from cointrader.signals.MACDSignal import MACDSignal

class Default(Strategy):
    def __init__(self, symbol: str, name='default'):
        super().__init__(symbol=symbol, name=name)
        self.macd = MACDSignal('macd', self._symbol, 12, 26, 9)

    def update(self, kline):
        self.macd.update(kline)

    def buy(self):
        if self.macd.ready() and self.macd.cross_up():
            return True
        return False

    def sell(self):
        if self.macd.ready() and self.macd.cross_down():
            return True
