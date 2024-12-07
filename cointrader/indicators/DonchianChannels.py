from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class DonchianChannels(Indicator):
    """Donchian Channels Indicator"""
    def __init__(self, name='donchian', period=20):
        super().__init__(name)
        self.period = period
        self.highs = deque(maxlen=period)  # Store the highs for the period
        self.lows = deque(maxlen=period)  # Store the lows for the period
        self._last_value = {"upper": None, "lower": None, "middle": None}
        self._ready = False

    def update(self, kline: Kline):
        # Assuming Kline has 'high' and 'low' attributes
        self.highs.append(kline.high)
        self.lows.append(kline.low)

        if len(self.highs) == self.period:
            upper_band = max(self.highs)
            lower_band = min(self.lows)
            middle_band = (upper_band + lower_band) / 2

            self._last_value = {
                "upper": upper_band,
                "lower": lower_band,
                "middle": middle_band
            }
            self._ready = True
        else:
            self._last_value = {"upper": None, "lower": None, "middle": None}
            self._ready = False

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def reset(self):
        self.highs.clear()
        self.lows.clear()
        self._last_value = {"upper": None, "lower": None, "middle": None}
        self._ready = False
        self._last_kline = None

    def ready(self) -> bool:
        return self._ready