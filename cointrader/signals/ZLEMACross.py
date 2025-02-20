from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.ZLEMA import ZLEMA
from cointrader.indicators.EMA import EMA

class ZLEMACross(Signal):
    def __init__(self, name='zlema', symbol=None, short_period=12, long_period=30):
        super().__init__(name, symbol)
        self.short_period = short_period
        self.long_period = long_period
        self.window = max(short_period, long_period)
        self.short_zlema = ZLEMA(name=f"{self._name}_short", period=self.short_period)
        self.long_zlema = EMA(name=f"{self._name}_long", period=self.long_period)
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
       
        if self.short_zlema.ready() and self.long_zlema.ready():
            if self._short_zlema_values[-1] > self._long_zlema_values[-1] and self._short_zlema_values[-2] <= self._long_zlema_values[-2]:
                self._cross_up = True
            elif self._short_zlema_values[-1] < self._long_zlema_values[-1] and self._short_zlema_values[-2] >= self._long_zlema_values[-2]:
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

    def increasing(self):
        return self._long_zlema_values[-1] > self._long_zlema_values[-2]
    
    def decreasing(self):
        return self._long_zlema_values[-1] < self._long_zlema_values[-2]

    def ready(self):
        return self.short_zlema.ready() and self.long_zlema.ready()

    def get_last_value(self):
        result = {
            "short_zlema": self.short_zlema,
            "long_zlema": self.long_zlema
        }
        return result
