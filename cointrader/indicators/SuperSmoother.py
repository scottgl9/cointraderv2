# Implements the Super Smoother Filter indicator.
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
import math

class SuperSmoother(Indicator):
    def __init__(self, name='super_smoother', period=12):
        super().__init__(name)
        self.period = period
        self.reset()

    def update(self, kline: Kline):
        price = kline.close

        if len(self.values) < 2:
            # Initialize with the first price value
            self.values.append(price)
        else:
            # Apply the Super Smoother Filter formula
            smoother_value = (
                self.b1 * price +
                self.b2 * self._last_price +
                self.b3 * self._prev_last_price -
                self.a1 * self.values[-1]
            )
            self.values.append(smoother_value)

        # Maintain a rolling window of values
        if len(self.values) > self.period:
            self.values.pop(0)

        # Update previous price values
        self._prev_last_price = self._last_price
        self._last_price = price

        # Store the last Kline and value
        self._last_kline = kline
        self._last_value = self.values[-1]

        return self._last_value

    def increasing(self) -> bool:
        return self.values[-1] > self.values[0]

    def decreasing(self) -> bool:
        return self.values[-1] < self.values[0]

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def reset(self):
        self.values = []
        self._last_price = 0
        self._prev_last_price = 0
        self._last_kline = None
        self._last_value = None
        self._compute_coefficients()

    def ready(self):
        return len(self.values) > 1

    def _compute_coefficients(self):
        """
        Computes the filter coefficients based on the period.
        """
        # Calculate the smoothing factor
        freq = 2 * math.pi / self.period
        alpha = (math.sin(freq) / (2 * 0.707)) / math.cos(freq)
        self.a1 = 2 * alpha
        self.b1 = alpha**2
        self.b2 = 2 * self.b1
        self.b3 = self.b1
