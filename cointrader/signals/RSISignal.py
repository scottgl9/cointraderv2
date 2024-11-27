from cointrader.common.Signal import Signal
from cointrader.indicators.RSI import RSI

class RSISignal(Signal):
    def __init__(self, period=14, overbought=70, oversold=30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.rsi = RSI(period)

    def update(self, kline):
        return self.rsi.update(kline)

    def cross_up(self):
        return False
    
    def cross_down(self):
        return False
    
    def above(self):
        return self.rsi > self.overbought
    
    def below(self):
        return self.rsi < self.oversold
    
    def ready(self):
        return self.rsi.ready()
