from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class FibonacciRetracement(Indicator):
    """Fibonacci Retracement Indicator"""
    def __init__(self, name='fibonacci', period=20):
        super().__init__(name)
        self.period = period
        self.highs = []  # Store the highs over the period
        self.lows = []   # Store the lows over the period
        self._last_value = None
        self._ready = False

    def update(self, kline: Kline):
        # Assuming Kline has 'high' and 'low' attributes
        self.highs.append(kline.high)
        self.lows.append(kline.low)

        # Maintain only the last 'period' values
        if len(self.highs) > self.period:
            self.highs.pop(0)
        if len(self.lows) > self.period:
            self.lows.pop(0)

        if len(self.highs) == self.period and len(self.lows) == self.period:
            highest_high = max(self.highs)
            lowest_low = min(self.lows)
            range = highest_high - lowest_low

            # Calculate Fibonacci levels
            levels = {
                "0%": lowest_low,
                "23.6%": lowest_low + 0.236 * range,
                "38.2%": lowest_low + 0.382 * range,
                "50%": lowest_low + 0.5 * range,
                "61.8%": lowest_low + 0.618 * range,
                "100%": highest_high
            }
            self._last_value = levels
            self._ready = True
        else:
            self._last_value = None
            self._ready = False

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def reset(self):
        self.highs.clear()
        self.lows.clear()
        self._last_value = None
        self._ready = False
        self._last_kline = None

    def ready(self) -> bool:
        return self._ready