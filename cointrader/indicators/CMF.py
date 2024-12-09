# This file contains the implementation of the Chaikin Money Flow (CMF) indicator.
from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class ChaikinMoneyFlow(Indicator):
    def __init__(self, name='chaikin_money_flow', period=20):
        """
        Initialize the Chaikin Money Flow (CMF) indicator.

        :param name: Name of the indicator.
        :param period: Number of periods over which to calculate the CMF.
        """
        super().__init__(name)
        self.period = period

        # Rolling window of CMF values
        self.mfv = deque(maxlen=self.period)
        self.volumes = deque(maxlen=self.period)

        # Internal state
        self.sum_mfv = 0.0
        self.sum_volume = 0.0
        self._last_kline = None
        self._last_value = None

    def reset(self):
        """
        Reset the CMF indicator to its initial state.
        """
        self.mfv.clear()
        self.volumes.clear()
        self.sum_mfv = 0.0
        self.sum_volume = 0.0
        self._last_kline = None
        self._last_value = None

    def update(self, kline: Kline):
        """
        Update the CMF indicator with a new Kline.

        :param kline: The new Kline data.
        :return: The updated CMF value or None if not enough data.
        """
        close = kline.close
        high = kline.high
        low = kline.low
        volume = kline.volume

        # Calculate Money Flow Multiplier (MFM)
        if high == low:
            mfm = 0.0  # Avoid division by zero
        else:
            mfm = ((close - low) - (high - close)) / (high - low)

        # Calculate Money Flow Volume (MFV)
        mfv = mfm * volume

        # Update rolling windows and sums
        if len(self.mfv) == self.period:
            # Remove the oldest values from the sums
            oldest_mfv = self.mfv.popleft()
            oldest_volume = self.volumes.popleft()
            self.sum_mfv -= oldest_mfv
            self.sum_volume -= oldest_volume

        # Add the new values
        self.mfv.append(mfv)
        self.volumes.append(volume)
        self.sum_mfv += mfv
        self.sum_volume += volume

        # Calculate CMF if enough data is available
        if len(self.mfv) == self.period and self.sum_volume != 0:
            cmf = self.sum_mfv / self.sum_volume
            self._last_value = cmf
        else:
            self._last_value = None

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        """
        Get the latest CMF value.

        :return: The latest CMF value or None.
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline used to compute CMF.

        :return: The last Kline object or None.
        """
        return self._last_kline

    def ready(self):
        """
        Check if the CMF indicator is ready to provide a value.

        :return: True if ready, False otherwise.
        """
        return len(self.mfv) == self.period and self.sum_volume != 0
