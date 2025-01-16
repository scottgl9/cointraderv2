# This file implements the Z-Score indicator. The Z-Score is a measure of how many standard deviations an observation is from the mean. 
# It is calculated as the difference between the observation and the mean divided by the standard deviation. 
# The Z-Score is useful for identifying outliers in a dataset. The Z-Score indicator is implemented as a subclass of the Indicator class.
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.SMA import SMA
from math import sqrt

class ZScore(Indicator):
    def __init__(self, name='zscore', period=14):
        Indicator.__init__(self, name)
        self.period = period
        self.sma = SMA(name=f"{name}_sma", period=period)  # Use the existing SMA indicator
        self.reset()

    def reset(self):
        self.prices = []
        self.sum_squares = 0.0  # Rolling sum of squared prices
        self._last_kline = None
        self._last_value = 0
        self.result = 0.0
        self.age = 0

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result

    def update_with_value(self, value: float):
        sma_value = self.sma.update_with_value(value)
        # Add the new value to the rolling list of prices
        if len(self.prices) < self.period:
            self.prices.append(float(value))
        else:
            # Replace the oldest value
            tail = self.prices[int(self.age)]
            self.prices[int(self.age)] = float(value)
            self.sum_squares -= tail ** 2  # Remove the squared contribution of the oldest value

        # Update rolling sum of squares and age
        self.sum_squares += float(value) ** 2
        self.age = (self.age + 1) % self.period

        # Calculate standard deviation
        variance = (self.sum_squares / len(self.prices)) - (sma_value ** 2)
        std_dev = sqrt(variance) if variance > 0 else 0

        # Calculate Z-Score
        if std_dev != 0:
            self.result = (value - sma_value) / std_dev
        else:
            self.result = 0.0

        self._last_value = self.result
        return self.result

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        # Ensure SMA is ready and we have enough data for Z-Score
        return self.sma.ready()
