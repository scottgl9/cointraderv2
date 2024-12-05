from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class SMA(Indicator):
    def __init__(self, name='sma', period=14):
        Indicator.__init__(self, name)
        self.period = period
        self.reset()

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result

    def update_with_value(self, value):
        tail = 0.0
        if len(self.prices) < self.period:
            tail = 0.0
            self.prices.append(float(value))
        else:
            tail = self.prices[int(self.age)]
            self.prices[int(self.age)] = float(value)

        self.sum += float(value) - tail
        if len(self.prices) != 0:
            self.result = self.sum / float(len(self.prices))
        self.age = (self.age + 1) % self.period
        self._last_value = self.result
        return self.result

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def reset(self):
        self.prices = []
        self._last_kline = None
        self._last_value = 0
        self.result = 0.0
        self.age = 0
        self.sum = 0.0

    def ready(self):
        return len(self.prices) == self.period
