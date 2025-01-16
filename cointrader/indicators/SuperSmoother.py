import math
from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class SuperSmoother(Indicator):
    def __init__(self, name='super_smoother', period=12):
        super().__init__(name)
        self.period = period
        self.reset()

    def reset(self):
        self.values = deque(maxlen=3)
        self._last_kline = None
        self._last_value = None
        self._last_price = None
        # Compute coefficients using Ehlers' formula
        self._compute_coefficients()

    def _compute_coefficients(self):
        freq = 1.414 * math.pi / self.period
        a1 = math.exp(-freq)
        self.c2 = 2 * a1 * math.cos(freq)
        self.c3 = -a1 * a1
        self.c1 = 1 - self.c2 - self.c3

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result

    def update_with_value(self, price: float):
        # Initialization phase
        if self._last_price is None:
            # Just store the first price, no smoothing yet
            self.values.append(price)
            self._last_price = price
            self._last_value = price
            return self._last_value
        elif len(self.values) == 1:
            # We have only one past smoothed value (seed),
            # The next smoothed value can be approximated:
            s = (self.c1 * (price + self._last_price) / 2.0) + self.c2 * self.values[-1] + self.c3 * self._last_price
            self.values.append(s)
            self._last_value = s
        else:
            # We have at least two previous smoothed values: s(n-1) = self.values[-1], s(n-2) = self.values[-2]
            # Apply the formula:
            s = (self.c1 * (price + self._last_price) / 2.0) + self.c2 * self.values[-1] + self.c3 * self.values[-2]
            self.values.append(s)
            self._last_value = s

        # Update last price and kline
        self._last_price = price
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        # We consider it ready once we have at least two smoothed values beyond initialization
        return len(self.values) >= 2

    def increasing(self) -> bool:
        if not self.ready():
            return False
        return self.values[-1] > self.values[-2]

    def decreasing(self) -> bool:
        if not self.ready():
            return False
        return self.values[-1] < self.values[-2]
