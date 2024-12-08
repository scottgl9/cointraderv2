from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.IchimokuCloud import IchimokuCloud

class IchimokuSignal(Signal):
    def __init__(self, name, symbol, win_short=9, win_med=26, win_long=52):
        super().__init__(name, symbol)
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.ichimoku = IchimokuCloud(win_short=self.win_short, win_med=self.win_med, win_long=self.win_long)
        self.reset()

    def reset(self):
        self.ichimoku.reset()
        self._cross_up = False
        self._cross_down = False

        # We'll keep track of recent Tenkan and Kijun values to detect crosses and momentum
        self.tenkan_values = deque(maxlen=2)
        self.kijun_values = deque(maxlen=2)

    def update(self, kline: Kline):
        result = self.ichimoku.update(kline)
        if result is None:
            return None

        tenkan = result['tenkan_sen']
        kijun = result['kijun_sen']

        # Store values
        self.tenkan_values.append(tenkan)
        self.kijun_values.append(kijun)

        if len(self.tenkan_values) < 2 or len(self.kijun_values) < 2:
            return None

        prev_tenkan = self.tenkan_values[-2]
        prev_kijun = self.kijun_values[-2]

        # Detect cross_up: Tenkan crosses above Kijun
        # Condition: previously Tenkan <= Kijun, now Tenkan > Kijun
        if prev_tenkan <= prev_kijun and tenkan > kijun:
            self._cross_up = True

        # Detect cross_down: Tenkan crosses below Kijun
        # Condition: previously Tenkan >= Kijun, now Tenkan < Kijun
        if prev_tenkan >= prev_kijun and tenkan < kijun:
            self._cross_down = True

        return result

    def ready(self):
        return self.ichimoku.ready()

    def increasing(self):
        # Tenkan increasing if current > previous
        if len(self.tenkan_values) < 2:
            return False
        return self.tenkan_values[-1] > self.tenkan_values[-2]

    def decreasing(self):
        # Tenkan decreasing if current < previous
        if len(self.tenkan_values) < 2:
            return False
        return self.tenkan_values[-1] < self.tenkan_values[-2]

    def above(self):
        # Tenkan above Kijun
        if len(self.tenkan_values) == 0 or len(self.kijun_values) == 0:
            return False
        return self.tenkan_values[-1] > self.kijun_values[-1]

    def below(self):
        # Tenkan below Kijun
        if len(self.tenkan_values) == 0 or len(self.kijun_values) == 0:
            return False
        return self.tenkan_values[-1] < self.kijun_values[-1]

    def cross_up(self):
        # Return True if a bullish cross (Tenkan > Kijun) just occurred
        result = self._cross_up
        self._cross_up = False
        return result

    def cross_down(self):
        # Return True if a bearish cross (Tenkan < Kijun) just occurred
        result = self._cross_down
        self._cross_down = False
        return result
