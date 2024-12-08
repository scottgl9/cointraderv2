from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from .SMA import SMA
import numpy as np

class BollingerBands(Indicator):
    def __init__(self, name='bb', period=20, std_dev=2):
        super().__init__(name)
        self.period = period
        self.std_dev_multiplier = std_dev
        self.sma = SMA(name + "_sma", period)
        self.reset()

    def reset(self):
        self.sma.reset()
        self.values = deque(maxlen=self.period)

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result

    def update_with_value(self, value: float):
        # Update the SMA and check if it's ready
        middle_band = self.sma.update_with_value(value)
        if not self.sma.ready():
            # Not enough data for SMA; bands cannot be calculated
            self.values.append(value)
            return self._last_value

        self.values.append(value)

        # Calculate standard deviation using sample standard deviation (ddof=1)
        std_dev = np.std(self.values, ddof=1)
        upper_band = middle_band + (self.std_dev_multiplier * std_dev)
        lower_band = middle_band - (self.std_dev_multiplier * std_dev)

        self._last_value = {
            'middle': middle_band,
            'upper': upper_band,
            'lower': lower_band
        }

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        return self.sma.ready() and len(self.values) == self.period
