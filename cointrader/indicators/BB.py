from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
import numpy as np

class BollingerBands(Indicator):
    def __init__(self, name, period, std_dev_multiplier):
        super().__init__(name)
        self.period = period
        self.std_dev_multiplier = std_dev_multiplier
        self.values = []
        self.timestamps = []
        self.klines = []

    def update(self, kline : Kline):
        self.klines.append(kline)
        self.timestamps.append(kline.ts)
        self.values.append(kline.close)

        if len(self.values) > self.period:
            self.values.pop(0)
            self.timestamps.pop(0)
            self.klines.pop(0)

        if len(self.values) == self.period:
            sma = np.mean(self.values)
            std_dev = np.std(self.values)
            upper_band = sma + (self.std_dev_multiplier * std_dev)
            lower_band = sma - (self.std_dev_multiplier * std_dev)
            self._last_value = tuple(sma, upper_band, lower_band)
        else:
            self._last_value = tuple(None, None, None)
        
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_timestamp(self):
        return self.timestamps[-1] if self.timestamps else None
    
    def get_last_kline(self):
        return self.klines[-1] if self.klines else None
    
    def reset(self):
        self.values = []
        self.timestamps = []
        self.klines = []

    def ready(self):
        return len(self.values) == self.period