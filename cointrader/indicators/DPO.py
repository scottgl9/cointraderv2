# This file contains the implementation of the Detrended Price Oscillator (DPO) indicator.
from collections import deque
from math import floor
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.SMA import SMA  # Assuming SMA is implemented as provided earlier

class DetrendedPriceOscillator(Indicator):
    def __init__(self, name='dpo', period=20):
        """
        Initialize the Detrended Price Oscillator.

        :param name: Name of the indicator.
        :param period: Lookback period for the SMA.
        """
        super().__init__(name)
        self.period = period
        self.shift = floor(self.period / 2) + 1  # Shift forward by n/2 +1
        self.total_length = self.period + self.shift

        # Deque to store closing prices
        self.closes = deque(maxlen=self.total_length)

        # SMA instance to compute the moving average
        self.sma = SMA(name=f'sma_{self.period}', period=self.period)

        # Deque to store SMA values for shifting
        self.sma_values = deque(maxlen=self.shift)

        self._last_value = None
        self._last_kline = None

    def reset(self):
        """
        Reset the internal state of the DPO indicator.
        """
        self.closes.clear()
        self.sma.reset()
        self.sma_values.clear()
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        """
        Update the DPO with a new Kline.

        :param kline: New kline data.
        :return: The latest DPO value or None if not enough data.
        """
        close = kline.close
        self.closes.append(close)

        # Update SMA with the latest close
        sma_val = self.sma.update_with_value(close)

        # Once SMA is ready, append it to sma_values deque
        if self.sma.ready():
            self.sma_values.append(sma_val) #self.sma.get_last_value())

        # Once we have enough SMA values to cover the shift, compute DPO
        if len(self.sma_values) == self.shift:
            # The SMA corresponding to the shifted period
            shifted_sma = self.sma_values.popleft()
            dpo = close - shifted_sma
            self._last_value = dpo
        else:
            # Not enough data to compute DPO yet
            self._last_value = None

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        """
        Get the latest DPO value.

        :return: Latest DPO value or None.
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline used to compute DPO.

        :return: Last Kline object or None.
        """
        return self._last_kline

    def ready(self):
        """
        Check if the DPO indicator has enough data to provide a value.

        :return: True if ready, False otherwise.
        """
        #return len(self.closes) == self.total_length and self.sma.ready() and len(self.sma_values) == self.shift
        return self._last_value is not None
