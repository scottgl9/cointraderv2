from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from .SMA import SMA
import numpy as np

class BollingerBands(Indicator):
    def __init__(self, name, period, std_dev_multiplier):
        super().__init__(name)
        self.period = period
        self.std_dev_multiplier = std_dev_multiplier
        self.sma = SMA(name + "_sma", period)
        self.reset()

    def update(self, kline : Kline):
        self.timestamps.append(kline.ts)
        self.values.append(kline.close)

        if len(self.values) > self.period:
            self.values.pop(0)
            self.timestamps.pop(0)
            self.klines.pop(0)

        sma_value = self.sma.update(kline)
        upper_band = 0.0
        lower_band = 0.0

        if len(self.values) == self.period:
            std_dev = np.std(self.values)
            upper_band = sma_value + (self.std_dev_multiplier * std_dev)
            lower_band = sma_value - (self.std_dev_multiplier * std_dev)

        self._last_value = {
            'sma': sma_value,
            'upper_band': upper_band,
            'lower_band': lower_band
        }

        self._last_kline = kline

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_timestamp(self):
        return self.timestamps[-1] if self.timestamps else None

    def get_last_kline(self):
        return self._last_kline
    
    def reset(self):
        self.sma.reset()
        self.values = []
        self.timestamps = []

    def ready(self):
        return len(self.values) == self.period
