from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class ZLEMA(Indicator):
    def __init__(self, name='zlema', period=12):
        super().__init__(name)
        self.period = period
        self.multiplier = 2 / (period + 1)
        self.reset()

    def reset(self):
        self.values = deque(maxlen=self.period)
        self.prices = deque(maxlen=self.period)

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result

    def update_with_value(self, value: float):
        if len(self.values) == 0:
            # Initialize the ZLEMA with the first price
            self.values.append(value)
        else:
            # Calculate the lag
            lag = (self.period - 1) // 2

            # Adjust the price to remove lag
            if len(self.prices) > lag:
                lagged_price = 2 * value - self.prices[-lag - 1]
            else:
                lagged_price = value

            # Calculate the ZLEMA
            zlema_value = (lagged_price - self.values[-1]) * self.multiplier + self.values[-1]
            self.values.append(zlema_value)

        # Store the last Kline and value
        self._last_value = self.values[-1]

        # Keep a list of all prices to manage the lag calculation
        self.prices.append(value)
        return self._last_value

    def increasing(self) -> bool:
        return self.values[-1] > self.values[0]

    def decreasing(self) -> bool:
        return self.values[-1] < self.values[0]

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        return len(self.values) == self.period
