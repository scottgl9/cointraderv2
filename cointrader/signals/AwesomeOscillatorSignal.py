from cointrader.indicators.AO import AwesomeOscillator
from cointrader.common.Signal import Signal
from collections import deque

class AwesomeOscillatorSignal(Signal):
    def __init__(self, name='ao_signal', symbol=None, short_period=5, long_period=34):
        Signal.__init__(self, name, symbol)
        self.ao = AwesomeOscillator(short_period=short_period, long_period=long_period)
        self._values = deque(maxlen=2)

    def reset(self):
        self.ao.reset()
        self._cross_down = False
        self._cross_up = False

    def update(self, kline):
        ao_value = self.ao.update(kline)
        if not self.ready():
            return
        self._values.append(ao_value)
        
        if self._values[-1] >= 0 and self._values[-2] < 0:
            self._cross_up = True
            self._cross_down = False

        if self._values[-1] <= 0 and self._values[-2] > 0:
            self._cross_up = False
            self._cross_down = True

    def cross_up(self):
        return self._cross_up
    
    def cross_down(self):
        return self._cross_down

    def ready(self):
        return self.ao.ready() and len(self._values) == 2
