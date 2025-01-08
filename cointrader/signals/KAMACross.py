from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.EMA import EMA
from cointrader.indicators.KAMA import KAMA

class KAMACross(Signal):
    def __init__(self, name='kama', symbol=None, short_period=12, long_period=24):
        super().__init__(name, symbol)
        self.short_period = short_period
        self.long_period = long_period
        self.window = max(short_period, long_period)
        self.short_kama = KAMA(f"{self._name}_short", self.short_period)
        self.long_kama = KAMA(f"{self._name}_long", self.long_period)
        self.reset()

    def reset(self):
        self.short_kama.reset()
        self.long_kama.reset()
        self._cross_up = False
        self._cross_down = False
        self._short_kama_values = deque(maxlen=self.window)
        self._long_kama_values = deque(maxlen=self.window)

    def update(self, kline: Kline):
        short_kama_value = self.short_kama.update(kline)
        long_kama_value = self.long_kama.update(kline)

        if short_kama_value is None or long_kama_value is None:
            return
        self._short_kama_values.append(short_kama_value)
        self._long_kama_values.append(long_kama_value)

        if not self.ready():
            return

        if self._short_kama_values[-1] > self._long_kama_values[-1] and self._short_kama_values[-2] <= self._long_kama_values[-2]:
            self._cross_up = True
        elif self._short_kama_values[-1] < self._long_kama_values[-1] and self._short_kama_values[-2] >= self._long_kama_values[-2]:
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
        if not self.ready():
            return False
        return self._short_kama_values[-1] > self._long_kama_values[-1]

    def below(self):
        if not self.ready():
            return False
        return self._short_kama_values[-1] < self._long_kama_values[-1]

    def increasing(self):
        if not self.ready():
            return False
        return self._short_kama_values[-1] > self._short_kama_values[-2]

    def decreasing(self):
        if not self.ready():
            return False
        return self._short_kama_values[-1] < self._short_kama_values[-2]

    def ready(self):
        return self.short_kama.ready() and self.long_kama.ready() and len(self._short_kama_values) >= 2

    def get_last_value(self):
        result = {
            "short_kama": self.short_kama,
            "long_kama": self.long_kama
        }
        return result
