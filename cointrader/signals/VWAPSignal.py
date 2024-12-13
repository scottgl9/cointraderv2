# Signal based on VWAP indicator
from collections import deque
from cointrader.common.Signal import Signal
from cointrader.indicators.VWAP import VWAP

class VWAPSignal(Signal):
    def __init__(self, name='vwap', symbol=None, period=14):
        super().__init__(name, symbol)
        self.period = period
        self.vwap = VWAP(period)
        self._last_close = None
        self._prev_last_close = None
        self.reset()

    def reset(self):
        self.vwap.reset()
        self._values = deque(maxlen=self.period)

    def update(self, kline):
        result = self.vwap.update(kline)
        self._values.append(result)
        self._prev_last_close = self._last_close
        self._last_close = kline.close

    def cross_up(self):
        if not self.ready() or self._prev_last_close is None:
            return False
        if self._values[-2] > self._prev_last_close and self._values[-1] <= self._last_close:
            return True
        return False

    def cross_down(self):
        if not self.ready() or self._prev_last_close is None:
            return False
        if self._values[-2] < self._prev_last_close and self._values[-1] >= self._last_close:
            return True
        return False

    def above(self):
        if not self.ready() or self._last_close is None:
            return False
        return self._last_close > self._values[-1]
    
    def below(self):
        if not self.ready():
            return False
        return self._last_close < self._values[-1]

    def increasing(self):
        if not self.ready():
            return False
        return self._values[-2] < self._values[-1]

    def decreasing(self):
        if not self.ready():
            return False
        return self._values[-2] > self._values[-1]

    def ready(self):
        return self.vwap.ready()
