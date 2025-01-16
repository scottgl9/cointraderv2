# Implements the Rate of Change (ROC) indicator
from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class ROC(Indicator):
    def __init__(self, name='roc', period=14, **kwargs):
        super().__init__(name, **kwargs)
        self.period = period
        self._values = deque(maxlen=self.period)
        self.reset()

    def ready(self) -> bool:
        return self._last_value is not None

    def reset(self):
        self._last_value = None
        self._last_kline = None
        self._values.clear()

    def update(self, kline: Kline) -> float:
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result
    
    def update_with_value(self, value) -> float:
        self._values.append(value)

        if len(self._values) < self.period:
            return None

        prev_value = self._values[0]
        if prev_value != 0:
            self._last_value = ((value - prev_value) / prev_value) * 100.0
        else:
            self._last_value = None
        return self._last_value

    def above(self) -> bool:
        if not self.ready():
            return False
        return self._last_value > 0

    def below(self) -> bool:
        if not self.ready():
            return False
        return self._last_value < 0

    def increasing(self) -> bool:
        if not self.ready():
            return False
        return self._values[-1] > self._values[-2]

    def decreasing(self) -> bool:
        if not self.ready():
            return False
        return self._values[-1] < self._values[-2]

    def get_last_value(self) -> float:
        return self._last_value

    def get_last_kline(self) -> Kline:
        return self._last_kline
