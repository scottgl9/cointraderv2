# Signal based on the Rate of Change (ROC) indicator
from collections import deque
from cointrader.common.Signal import Signal
from cointrader.indicators.ROC import ROC

class ROCSignal(Signal):
    def __init__(self, name='roc', symbol=None, period=14):
        super().__init__(name, symbol)
        self.period = period
        self.roc = ROC(period)
        self.reset()

    def reset(self):
        self.roc.reset()
        self._values = deque(maxlen=self.period)
        self._cross_down = False
        self._cross_up = False

    def update(self, kline):
        result = self.roc.update(kline)
        if result is None:
            return
        self._values.append(result)
        if len(self._values) == self.period:
            if self._values[0] < 0 and self._values[-1] > 0:
                self._cross_up = True
            elif self._values[0] > 0 and self._values[-1] < 0:
                self._cross_down = True

    def cross_up(self):
        result = self._cross_up
        self._cross_up = False
        return result
    
    def cross_down(self):
        result = self._cross_down
        self._cross_down = False
        return result

    def above(self):
        return self.roc.above()
    
    def below(self):
        return self.roc.below()

    def increasing(self):
        return self.roc.increasing()

    def decreasing(self):
        return self.roc.decreasing()

    def ready(self):
        return self.roc.ready()
