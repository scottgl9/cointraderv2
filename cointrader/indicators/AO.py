# This file contains the implementation of the Awesome Oscillator (AO) indicator.
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.SMA import SMA

class AwesomeOscillator(Indicator):
    def __init__(self, name='awesome_oscillator', short_period=5, long_period=34):
        """
        Initialize the Awesome Oscillator with short-term and long-term SMA periods.
        """
        Indicator.__init__(self, name)
        self.short_sma = SMA(name='short_sma', period=short_period)
        self.long_sma = SMA(name='long_sma', period=long_period)
        self._last_value = 0.0
        self._last_kline = None

    def reset(self):
        """
        Reset the Awesome Oscillator and its dependent SMAs.
        """
        self.short_sma.reset()
        self.long_sma.reset()
        self._last_value = 0.0
        self._last_kline = None

    def update(self, kline: Kline):
        """
        Update the Awesome Oscillator with a new Kline.
        """
        # Calculate the median price for the given Kline
        median_price = (kline.high + kline.low) / 2

        # Update the short-term and long-term SMAs with the median price
        short_value = self.short_sma.update_with_value(median_price)
        long_value = self.long_sma.update_with_value(median_price)

        # Calculate the Awesome Oscillator value
        if self.short_sma.ready() and self.long_sma.ready():
            self._last_value = short_value - long_value
        else:
            self._last_value = None  # Not ready to calculate yet

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        """
        Get the last calculated Awesome Oscillator value.
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline used in the calculation.
        """
        return self._last_kline

    def reset(self):
        """
        Reset the Awesome Oscillator and its dependent SMAs.
        """
        self.short_sma.reset()
        self.long_sma.reset()
        self._last_value = 0.0
        self._last_kline = None

    def ready(self):
        """
        Check if the Awesome Oscillator is ready for calculation.
        """
        return self.short_sma.ready() and self.long_sma.ready() and self._last_value is not None
