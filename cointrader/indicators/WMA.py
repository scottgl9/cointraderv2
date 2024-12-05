from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class WMA(Indicator):
    """Weighted Moving Average used as a smoother."""
    def __init__(self, name='wma', period=14):
        super().__init__(name)
        self.period = period
        self.reset()

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result

    def update_with_value(self, value):
        self.values.append(value)
        if len(self.values) > self.period:
            self.values.pop(0)

        if len(self.values) < self.period:
            return None  # Not enough data for WMA

        weights = range(1, len(self.values) + 1)
        self._last_value = sum(v * w for v, w in zip(self.values, weights)) / sum(weights)
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def reset(self):
        self.values = []
        self._last_kline = None
    
    def ready(self) -> bool:
        return len(self.values) == self.period
