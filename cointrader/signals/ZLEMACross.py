from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.ZLEMA import ZLEMA

class ZLEMACross(Signal):
    def __init__(self, name, symbol, short_period, long_period):
        super().__init__(name, symbol)
        self.short_period = short_period
        self.long_period = long_period
        self.window = max(short_period, long_period)
        self.short_zlema = ZLEMA(f"{self._name}_short", self.short_period)
        self.long_zlema = ZLEMA(f"{self._name}_long", self.long_period)
        self.reset()

    def reset(self):
        self.short_zlema.reset()
        self.long_zlema.reset()
        self._cross_up = False
        self._cross_down = False
        self._short_zlema_values = deque(maxlen=self.window)
        self._long_zlema_values = deque(maxlen=self.window)

    def update(self, kline: Kline):
        short_zlema_value = self.short_zlema.update(kline)
        self._short_zlema_values.append(short_zlema_value)
        long_zlema_value = self.long_zlema.update(kline)
        self._long_zlema_values.append(long_zlema_value)
       
        if short_zlema_value > max(self._long_zlema_values) and min(self._short_zlema_values) < self._long_zlema_values[-1]:
            self._cross_up = True
        elif short_zlema_value < min(self._long_zlema_values) and max(self._short_zlema_values) > self._long_zlema_values[-1]:
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
        return self.short_zlema > self.long_zlema

    def below(self):
        return self.short_zlema < self.long_zlema

    def ready(self):
        return self.short_zlema.ready() and self.long_zlema.ready()

    def get_last_value(self):
        result = {
            "short_zlema": self.short_zlema,
            "long_zlema": self.long_zlema
        }
        return result
