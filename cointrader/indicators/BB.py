from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from .SMA import SMA
import numpy as np

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

    def update(self, kline: Kline):
        # Update the SMA and check if it's ready
        middle_band = self.sma.update(kline)
        if not self.sma.ready():
            # Not enough data for SMA; bands cannot be calculated
            self.values.append(kline.close)
            self._last_value = {
                'middle': None,
                'upper': None,
                'lower': None
            }
            self._last_kline = kline
            return self._last_value

        # Maintain a rolling window of 'self.period' closing prices
        self.values.append(kline.close)
        if len(self.values) > self.period:
            self.values.pop(0)

        # Calculate standard deviation using sample standard deviation (ddof=1)
        std_dev = np.std(self.values, ddof=1)
        upper_band = middle_band + (self.std_dev_multiplier * std_dev)
        lower_band = middle_band - (self.std_dev_multiplier * std_dev)

        self._last_value = {
            'middle': middle_band,
            'upper': upper_band,
            'lower': lower_band
        }

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def reset(self):
        self.sma.reset()
        self.values = []

    def ready(self):
        return self.sma.ready() and len(self.values) == self.period
