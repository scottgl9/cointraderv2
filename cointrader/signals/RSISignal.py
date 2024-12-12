# Signal based on RSI indicator
from collections import deque
from cointrader.common.Signal import Signal
from cointrader.indicators.RSI import RSI

class RSISignal(Signal):
    def __init__(self, name='rsi', symbol=None, period=14, overbought=70, oversold=30):
        super().__init__(name, symbol)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.rsi = RSI(period)
        self.reset()

    def reset(self):
        self.rsi.reset()
        self._values = deque(maxlen=self.period)

    def update(self, kline):
        result = self.rsi.update(kline)
        self._values.append(result)

    def cross_up(self):
        return False
    
    def cross_down(self):
        return False
    
    def above(self):
        if not self.ready():
            return False
        return self._values[-1] > self.overbought
    
    def below(self):
        if not self.ready():
            return False
        return self._values[-1] < self.oversold

    def increasing(self):
        if not self.ready():
            return False
        if self._values[-2] < self._values[-1]:
            return True
        return False
    
    def decreasing(self):
        if not self.ready():
            return False
        if self._values[-2] > self._values[-1]:
            return True
        return False

    def ready(self):
        return self.rsi.ready()
