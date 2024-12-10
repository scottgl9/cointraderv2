from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.EMA import EMA

class EMACross(Signal):
    def __init__(self, name, symbol, short_period, long_period):
        super().__init__(name, symbol)
        self.short_period = short_period
        self.long_period = long_period
        self.window = max(short_period, long_period)
        self.short_ema = EMA(f"{self._name}_short", self.short_period)
        self.long_ema = EMA(f"{self._name}_long", self.long_period)
        self.reset()

    def reset(self):
        self.short_ema.reset()
        self.long_ema.reset()
        self._cross_up = False
        self._cross_down = False
        self._short_ema_values = deque(maxlen=self.window)
        self._long_ema_values = deque(maxlen=self.window)

    def update(self, kline: Kline):
        short_ema_value = self.short_ema.update(kline)
        long_ema_value = self.long_ema.update(kline)

        self._short_ema_values.append(short_ema_value)
        self._long_ema_values.append(long_ema_value)
        
        if self.short_ema.ready() and self.long_ema.ready():
            if short_ema_value > max(self._long_ema_values) and min(self._short_ema_values) < self._long_ema_values[-1]:
                self._cross_up = True
            elif short_ema_value < min(self._long_ema_values) and max(self._short_ema_values) > self._long_ema_values[-1]:
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
        return self.short_ema.get_last_value() > self.long_ema.get_last_value()

    def below(self):
        return self.short_ema.get_last_value() < self.long_ema.get_last_value()
    
    def increasing(self):
        return self._short_ema_values[-1] > self._short_ema_values[0]

    def decreasing(self):
        return self._short_ema_values[-1] < self._short_ema_values[0]

    def ready(self):
        return self.short_ema.ready() and self.long_ema.ready()

    def get_last_value(self):
        result = {
            "short_ema": self.short_ema,
            "long_ema": self.long_ema
        }
        return result
