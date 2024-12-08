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
        self.values = deque(maxlen=self.period)

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result

    def update_with_value(self, value: float):
        if len(self.values) == 0:
            self.values.append(value)
        else:
            ema_value = (value - self.values[-1]) * self.multiplier + self.values[-1]
            self.values.append(ema_value)
        
        self._last_value = self.values[-1]
        return self._last_value

    def increasing(self) -> bool:
        return self.values[-1] > self.values[0]

    def decreasing(self) -> bool:
        return self.values[-1] < self.values[0]

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        return len(self.values) == self.period