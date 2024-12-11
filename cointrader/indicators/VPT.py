# This file implements the Volume Price Trend (VPT) indicator
# The VPT indicator is used to determine the volume of a security traded at a certain price
# It is based on the idea that volume precedes price movement
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class VPT(Indicator):
    def __init__(self, name='vpt'):
        super().__init__(name)
        self.reset()

    def reset(self):
        self._last_value = 0
        self._last_kline = None
        self._last_close = None

    def update(self, kline: Kline):
        if not self._last_close:
            self._last_close = kline.close
            return self._last_value

        self._last_value += kline.volume * (kline.close - self._last_close) / self._last_close

        self._last_kline = kline.copy()
        self._last_close = kline.close

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline
    
    def ready(self):
        return self._last_kline is not None
