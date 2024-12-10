# This file is a prototype for a moving average normalization indicator.
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.SMA import SMA

class MANormalize(Indicator):
    def __init__(self, period: int):
        self.period = period
        self._sma = SMA(period)
        self._last_value = None
        self._last_kline = None

    def update(self, kline : Kline):
        self._sma.update(kline)
        if not self._sma.ready():
            return self._last_value
        self._last_value = kline.close - self._sma.get_last_value()
        return self._last_value

    def ready(self) -> bool:
        return self._sma.ready() and self._last_value is not None
