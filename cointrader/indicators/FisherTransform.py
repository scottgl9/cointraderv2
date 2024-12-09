from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
import math

class FisherTransform(Indicator):
    def __init__(self, name='fisher_transform', length=9):
        super().__init__(name)
        self.length = length
        self.highs = deque(maxlen=length)
        self.lows = deque(maxlen=length)
        self.value = None
        self.prev_x = 0.0
        self.fisher = 0.0
        self.signal = 0.0  # optional signal line if desired

    def update(self, kline: Kline):
        """Update the Fisher Transform indicator with new price data."""
        # Add the new data points
        self.highs.append(kline.high)
        self.lows.append(kline.low)

        # Only compute if we have enough data
        if len(self.highs) < self.length:
            return None

        # Median price of the current candle
        median_price = (kline.high + kline.low) / 2.0

        # Normalize median price over lookback period
        min_low = min(self.lows)
        max_high = max(self.highs)
        if max_high == min_low:
            # Avoid division by zero if all highs and lows are the same.
            x = 0.0
        else:
            x = 0.66 * ((median_price - min_low) / (max_high - min_low) - 0.5) + 0.67 * self.prev_x

        # Fisher transform
        # Bound x to avoid math domain errors due to floating point precision
        if x > 0.9999:
            x = 0.9999
        if x < -0.9999:
            x = -0.9999

        fisher = 0.5 * math.log((1.0 + x) / (1.0 - x))

        # Store values for next iteration
        self.prev_x = x
        self.signal = self.fisher  # shift previous fisher into signal line if desired
        self.fisher = fisher

        self.value = {
            'fisher': self.fisher,
            'signal': self.signal
        }

        return self.value

    def get_last_value(self):
        return self.value

    def ready(self):
        return self.value is not None
