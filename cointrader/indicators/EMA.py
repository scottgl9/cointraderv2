from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class EMA(Indicator):
    def __init__(self, name='ema', period=12):
        super().__init__(name)
        self.period = period
        self.multiplier = 2 / (period + 1)
        self.reset()

    def reset(self):
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result

    def update_with_value(self, value: float):
        if self._last_value is None:
            self._last_value = value
        else:
            self._last_value = (value - self._last_value) * self.multiplier + self._last_value

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        return self._last_value is not None
