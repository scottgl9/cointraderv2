from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class ATR(Indicator):
    def __init__(self, name='atr', period=14):
        super().__init__(name)
        self.window = period
        self.reset()

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close, kline.low, kline.high)
        self._last_kline = kline
        return result

    def update_with_value(self, close, low, high):
        if not self.count:
            tr = high - low
        else:
            tr = max([high - low, abs(high - self.last_close), abs(low - self.last_close)])
        if self.count < self.window - 1:
            self._tr_sum += tr
            self.count += 1
        elif not self.atr:
            self._tr_sum += tr
            self.atr = self._tr_sum / self.window
            self.count += 1
        else:
            self.prior_atr = self.atr
            self.atr = ((self.prior_atr * float(self.window - 1)) + tr) / self.window

        self.last_close = close
        self.result = self.atr
        self._last_value = self.result
        return self.result

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def reset(self):
        self.result = 0.0
        self.last_close = 0.0
        self._tr_sum = 0
        self.count = 0
        self.atr = 0
        self.prior_atr = 0
        self._last_value = None

    def ready(self) -> bool:
        return self.count >= self.window
