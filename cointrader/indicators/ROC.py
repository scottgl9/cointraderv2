# Implements the Rate of Change (ROC) indicator
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class ROC(Indicator):
    def __init__(self, name, period, **kwargs):
        super().__init__(name, **kwargs)
        self.period = period
        self.reset()

    def ready(self) -> bool:
        return self._last_value is not None

    def reset(self):
        self._last_value = None

    def update(self, kline: Kline) -> dict:
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result
    
    def update_with_value(self, value) -> float:
        if self._last_value is None:
            self._last_value = value
            return None
        
        prev_price = self._last_value
        if prev_price != 0:
            self._last_value = ((value - prev_price) / prev_price) * 100.0
        else:
            self._last_value = None
        return self._last_value

    def increasing(self) -> bool:
        if not self.ready():
            return False
        return self._last_value > 0

    def decreasing(self) -> bool:
        if not self.ready():
            return False
        return self._last_value < 0

    def get_last_value(self) -> float:
        return self._last_value

    def get_last_kline(self) -> Kline:
        return self._last_kline
