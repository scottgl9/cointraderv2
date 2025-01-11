# This file contains the WILLiams %R indicator
from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class WILLR(Indicator):
    def __init__(self, name='willr', period=14):
        super().__init__(name)
        self.window = period
        self.highs = deque(maxlen=period)
        self.lows = deque(maxlen=period)
        self.result = 0.0
        self._last_value = None

    def reset(self):
        self.highs.clear()
        self.lows.clear()
        self.result = 0.0
        self._last_value = None

    def update(self, kline: Kline):
        # Update high and low deque
        self.highs.append(kline.high)
        self.lows.append(kline.low)

        if len(self.highs) == self.window and len(self.lows) == self.window:
            highest_high = max(self.highs)
            lowest_low = min(self.lows)

            # Avoid division by zero
            if highest_high - lowest_low == 0:
                self.result = 0.0
            else:
                self.result = ((highest_high - kline.close) / (highest_high - lowest_low)) * -100

            self._last_value = self.result

        return self.result

    def get_last_value(self):
        return self._last_value

    def ready(self) -> bool:
        return len(self.highs) == self.window
