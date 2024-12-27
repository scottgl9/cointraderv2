from cointrader.indicators.CCI import CCI
from cointrader.common.Signal import Signal
from collections import deque

class CCISignal(Signal):
    def __init__(self, name='cci_signal', symbol=None, period=20, overbought=100, oversold=-100):
        Signal.__init__(self, name, symbol)
        self.cci = CCI(period=period)
        self._overbought = overbought
        self._oversold = oversold
        self._values = deque(maxlen=2)

    def reset(self):
        self.cci.reset()
        self._values.clear()

    def update(self, kline):
        result = self.cci.update(kline)
        self._values.append(result)

    def above(self):
        if not self.ready():
            return False
        return self._values[-1] > self._overbought
    
    def below(self):
        if not self.ready():
            return False
        return self._values[-1] < self._oversold

    def increasing(self):
        return self._values[-1] > self._values[-2]
    
    def decreasing(self):
        return self._values[-1] < self._values[-2]

    def ready(self):
        return self.cci.ready() and len(self._values) == 2
