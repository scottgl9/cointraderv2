from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class OBV(Indicator):
    def __init__(self, name):
        super().__init__(name)
        self.reset()

    def reset(self):
        self._last_value = 0
        self._last_kline = None

    def update(self, kline: Kline):
        if not self.ready():
            self._last_value = 0
        else:
            if kline.close > self._last_kline.close:
                self._last_value += kline.volume
            elif kline.close < self._last_kline.close:
                self._last_value -= kline.volume

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline
    
    def ready(self):
        return self._last_kline is not None
