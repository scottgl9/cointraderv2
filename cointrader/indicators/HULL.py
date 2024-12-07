from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from math import sqrt

class HMA(Indicator):
    """Hull Moving Average."""
    def __init__(self, name='hma', period=14):
        super().__init__(name)
        self.period = period
        self.sqrt_period = int(sqrt(period))
        self.wma_full = WMA(name=f'{name}_wma_full', period=period)
        self.wma_half = WMA(name=f'{name}_wma_half', period=period // 2)
        self.wma_hull = WMA(name=f'{name}_wma_hull', period=self.sqrt_period)
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        # Update intermediate WMAs
        wma_half_value = self.wma_half.update(kline)
        wma_full_value = self.wma_full.update(kline)

        if wma_half_value is not None and wma_full_value is not None:
            # Compute the difference: (2 * WMA_half) - WMA_full
            diff_value = (2 * wma_half_value) - wma_full_value

            # Update the final WMA with the difference
            self._last_value = self.wma_hull.update_with_value(diff_value)
            self._last_kline = kline

        return {"hma": self._last_value}

    def get_last_value(self):
        return self._last_value

    def ready(self) -> bool:
        return self.wma_hull.ready()

    def reset(self):
        self.wma_full.reset()
        self.wma_half.reset()
        self.wma_hull.reset()
        self._last_value = None
        self._last_kline = None