from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.SMA import SMA

class SMACross(Signal):
    def __init__(self, name='sma', symbol=None, short_period=50, long_period=100):
        super().__init__(name, symbol)
        self.short_period = short_period
        self.long_period = long_period
        self.window = max(short_period, long_period)
        self.short_sma = SMA(f"{self._name}_short", self.short_period)
        self.long_sma = SMA(f"{self._name}_long", self.long_period)
        self.reset()

    def reset(self):
        self.short_sma.reset()
        self.long_sma.reset()
        self._cross_up = False
        self._cross_down = False
        self._short_sma_values = deque(maxlen=self.window)
        self._long_sma_values = deque(maxlen=self.window)

    def update(self, kline: Kline):
        short_sma_value = self.short_sma.update(kline)
        long_sma_value = self.long_sma.update(kline)

        self._short_sma_values.append(short_sma_value)
        self._long_sma_values.append(long_sma_value)
        
        if self.short_sma.ready() and self.long_sma.ready():
            if self._short_sma_values[-1] > self._long_sma_values[-1] and self._short_sma_values[-2] <= self._long_sma_values[-2]:
                self._cross_up = True
            elif self._short_sma_values[-1] < self._long_sma_values[-1] and self._short_sma_values[-2] >= self._long_sma_values[-2]:
                self._cross_down = True
        return

    def cross_up(self):
        result = self._cross_up
        self._cross_up = False
        return result
    
    def cross_down(self):
        result = self._cross_down
        self._cross_down = False
        return result

    def above(self):
        return self.short_sma.get_last_value() > self.long_sma.get_last_value()

    def below(self):
        return self.short_sma.get_last_value() < self.long_sma.get_last_value()
    
    def increasing(self):
        return self._short_sma_values[-1] > self._short_sma_values[-2]

    def decreasing(self):
        return self._short_sma_values[-1] < self._short_sma_values[-2]

    def ready(self):
        return self.short_sma.ready() and self.long_sma.ready()

    def get_last_value(self):
        result = {
            "short_sma": self.short_sma,
            "long_sma": self.long_sma
        }
        return result
