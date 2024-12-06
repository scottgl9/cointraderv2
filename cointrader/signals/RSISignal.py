from cointrader.common.Signal import Signal
from cointrader.indicators.RSI import RSI

class RSISignal(Signal):
    def __init__(self, period=14, overbought=70, oversold=30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.rsi = RSI(period)
        self._values = []

    def update(self, kline):
        result = self.rsi.update(kline)
        self._values.append(result)
        if len(self._values) > self.period:
            self._values.pop(0)

    def increasing(self):
        return self.rsi.increasing()
    
    def decreasing(self):
        return self.rsi.decreasing()

    def cross_up(self):
        return False
    
    def cross_down(self):
        return False
    
    def above(self):
        return self._values[-1] > self.overbought
    
    def below(self):
        return self._values[-1] < self.oversold

    def increasing(self):
        if self._values[0] < self._values[-1]:
            return True
        return False
    
    def decreasing(self):
        if self._values[0] > self._values[-1]:
            return True
        return False

    def ready(self):
        return self.rsi.ready()
