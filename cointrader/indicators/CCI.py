# This file contains the implementation of the Commodity Channel Index (CCI) indicator.
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.SMA import SMA  # Assuming SMA is implemented as provided
from collections import deque

class CCI(Indicator):
    def __init__(self, name='cci', period=20):
        """
        Initialize the Commodity Channel Index (CCI) indicator.
        """
        Indicator.__init__(self, name)
        self.period = period
        self.sma = SMA(name='sma', period=period)
        #self.prices = deque(maxlen=period)
        self.mean_values = deque(maxlen=period)
        self.reset()

    def reset(self):
        """
        Reset the CCI calculation.
        """
        self.sma.reset()
        #self.prices.clear()
        self.mean_values.clear()
        self._last_value = None
        self._last_kline = None

    def ready(self):
        """
        Check if the CCI is ready for calculation.
        """
        return self.sma.ready() and self._last_value is not None

    def update(self, kline: Kline):
        """
        Update the CCI with a new Kline.
        """
        # Calculate the Typical Price (TP)
        typical_price = (kline.high + kline.low + kline.close) / 3
        #self.prices.append(typical_price)

        # Update the SMA with the Typical Price
        sma_value = self.sma.update_with_value(typical_price)

        self.mean_values.append(abs(typical_price - sma_value))

        # Calculate CCI if enough data is available
        if self.sma.ready():
            #mean_deviation = sum(abs(tp - sma_value) for tp in self.prices) / self.period
            mean_deviation = sum(self.mean_values) / self.period
            if mean_deviation != 0:
                self._last_value = (typical_price - sma_value) / (0.015 * mean_deviation)
            else:
                self._last_value = None
        else:
            self._last_value = None

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        """
        Get the last calculated CCI value.
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline used in the calculation.
        """
        return self._last_kline
