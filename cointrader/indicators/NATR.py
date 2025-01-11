# This file is an implementation of the NATR (normalized ATR) indicator
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from .ATR import ATR

class NATR(Indicator):
    def __init__(self, name='natr', period=14):
        super().__init__(name)
        self.window = period
        self.atr = ATR(period=period)
        self.reset()

    def reset(self):
        self.atr.reset()
        self.result = 0.0
        self._last_value = None

    def update(self, kline: Kline):
        atr_value = self.atr.update(kline)
        if atr_value is not None and kline.close > 0:
            self.result = (atr_value / kline.close) * 100
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self.atr.get_last_kline()

    def ready(self) -> bool:
        return self.atr.ready()
