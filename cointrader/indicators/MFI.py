# This file contains the implementation of the Money Flow Index (MFI) indicator.
from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class MoneyFlowIndex(Indicator):
    def __init__(self, name='money_flow_index', period=14):
        """
        Initialize the Money Flow Index (MFI) indicator.

        :param name: Name of the indicator.
        :param period: Number of periods over which to calculate the MFI.
        """
        super().__init__(name)
        self.period = period

        # Rolling window of MFI values
        self.money_flows = deque(maxlen=self.period)
        self.reset()

    def reset(self):
        """
        Reset the MFI indicator to its initial state.
        """
        self.money_flows.clear()
        self._last_kline = None
        self._last_value = None

    def update(self, kline: Kline):
        """
        Update the MFI indicator with a new Kline.

        :param kline: The new Kline data.
        :return: The updated MFI value or None if not enough data.
        """
        close = kline.close
        high = kline.high
        low = kline.low
        volume = kline.volume

        typical_price = (high + low + close) / 3

        # Calculate Money Flow (MF)
        mf = typical_price * volume

        # Add new Money Flow to the rolling window
        self.money_flows.append(mf)

        # Calculate Positive and Negative Money Flows
        positive_mf = sum([mf for mf in self.money_flows if mf >= 0])
        negative_mf = sum([mf for mf in self.money_flows if mf < 0])

        # Calculate Money Flow Ratio (MFR)
        if negative_mf == 0:
            mfr = 100.0  # Avoid division by zero
        else:
            mfr = positive_mf / negative_mf

        # Calculate Money Flow Index (MFI)
        mfi = 100 - 100 / (1 + mfr)

        # Update internal state
        self._last_kline = kline.copy()
        self._last_value = mfi

        return mfi

    def get_last_value(self):
        return self._last_value
    
    def get_last_kline(self):
        return self._last_kline
    
    def ready(self):
        return len(self.money_flows) == self.period
