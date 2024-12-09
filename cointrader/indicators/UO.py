# This file contains the implementation of the Ultimate Oscillator (UO) indicator.
from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class UltimateOscillator(Indicator):
    def __init__(self, name='ultimate_oscillator', short_period=7, medium_period=14, long_period=28):
        super().__init__(name)
        self.short_period = short_period
        self.medium_period = medium_period
        self.long_period = long_period

        # Deques to store BP and TR values
        self.bp_values = deque(maxlen=self.long_period)  # store at least 28 bars
        self.tr_values = deque(maxlen=self.long_period)

        self._last_value = None
        self._last_kline = None
        self._prev_close = None

    def update(self, kline: Kline):
        if self._prev_close is None:
            # Can't calculate BP and TR on the first bar, just store close
            self._prev_close = kline.close
            self._last_kline = kline
            return None

        # Compute BP and TR
        prev_close = self._prev_close
        bp = kline.close - min(kline.low, prev_close)
        tr = max(kline.high, prev_close) - min(kline.low, prev_close)

        self.bp_values.append(bp)
        self.tr_values.append(tr)

        self._prev_close = kline.close
        self._last_kline = kline

        # Only compute UO if we have at least `long_period` bars
        if len(self.bp_values) < self.long_period:
            self._last_value = None
            return None

        # Compute averages over the three periods
        # We have at least 28 bars stored
        def avg_ratio(period):
            bp_sum = sum(list(self.bp_values)[-period:])
            tr_sum = sum(list(self.tr_values)[-period:])
            if tr_sum == 0:
                return 0
            return bp_sum / tr_sum

        avg_short = avg_ratio(self.short_period)
        avg_med = avg_ratio(self.medium_period)
        avg_long = avg_ratio(self.long_period)

        # Calculate Ultimate Oscillator
        # Weighted sum: (4*avg_short + 2*avg_med + 1*avg_long) / (4+2+1)
        uo = 100 * ( (4.0 * avg_short) + (2.0 * avg_med) + (1.0 * avg_long) ) / (4.0 + 2.0 + 1.0)

        self._last_value = uo
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        # Ready when we have enough bars to compute the full periods (at least 28 bars)
        return len(self.bp_values) == self.long_period
