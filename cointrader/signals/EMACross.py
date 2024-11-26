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

    def update(self, kline: Kline):
        short_ema_value = self.short_ema.update(kline)
        long_ema_value = self.long_ema.update(kline)
        result = {
            "short_ema": short_ema_value,
            "long_ema": long_ema_value
        }

        self._values.append(result)

        if len(self._values) > self.window:
            self._values.pop(0)

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
        return self.short_ema > self.long_ema

    def below(self):
        return self.short_ema < self.long_ema

    def ready(self):
        return self.short_ema.ready() and self.long_ema.ready()

    def get_last_value(self):
        result = {
            "short_ema": self.short_ema,
            "long_ema": self.long_ema
        }
        return result

    def reset(self):
        self.short_ema.reset()
        self.long_ema.reset()
        self._cross_up = False
        self._cross_down = False