from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class IchimokuCloud(Indicator):
    def __init__(self, name='ichimoku_cloud', win_short=9, win_med=26, win_long=52):
        super().__init__(name)
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.highs = deque(maxlen=win_long)
        self.lows = deque(maxlen=win_long)
        self.closes = deque(maxlen=win_long+1)

        self._last_value = None
        self._last_kline = None

    def reset(self):
        self.highs.clear()
        self.lows.clear()
        self.closes.clear()
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        # Add new data
        self.highs.append(kline.high)
        self.lows.append(kline.low)
        self.closes.append(kline.close)

        # We can only calculate once we have enough data:
        if len(self.highs) < self.win_long:
            return None

        # Compute Tenkan-sen
        high_9 = max(list(self.highs)[-self.win_short:])
        low_9 = min(list(self.lows)[-self.win_short:])
        tenkan_sen = (high_9 + low_9) / 2

        # Compute Kijun-sen
        high_26 = max(list(self.highs)[-self.win_med:])
        low_26 = min(list(self.lows)[-self.win_med:])
        kijun_sen = (high_26 + low_26) / 2

        # Compute Senkou Span A (Leading line)
        senkou_span_a = (tenkan_sen + kijun_sen) / 2

        # Compute Senkou Span B (Leading line)
        high_52 = max(self.highs)
        low_52 = min(self.lows)
        senkou_span_b = (high_52 + low_52) / 2

        # Compute Chikou Span (Lagging line)
        # Chikou is the current close shifted back 26 periods (if possible)
        chikou_span = None
        if len(self.closes) > self.win_med:
            chikou_span = self.closes[-self.win_med]

        self._last_value = {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span
        }

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def ready(self):
        return self._last_value is not None
