# Signal based on OBV indicator
from collections import deque
from cointrader.common.Signal import Signal
from cointrader.indicators.OBV import OBV

class OBVSignal(Signal):
    def __init__(self, name='obv', symbol=None, period=14):
        super().__init__(name, symbol)
        self.period = period
        self.obv = OBV()
        self.reset()

    def reset(self):
        self.obv.reset()
        self._values = deque(maxlen=self.period)

    def update(self, kline):
        result = self.obv.update(kline)
        self._values.append(result)

    def cross_up(self):
        return False
    
    def cross_down(self):
        return False
    
    def above(self):
        return self._values[-1] > 0
    
    def below(self):
        return self._values[-1] < 0

    def increasing(self):
        if self._values[-2] < self._values[-1]:
            return True
        return False
    
    def decreasing(self):
        if self._values[-2] > self._values[-1]:
            return True
        return False

    def ready(self):
        return len(self._values) == self.period
