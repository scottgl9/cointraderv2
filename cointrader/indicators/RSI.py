from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class RSI(Indicator):
    def __init__(self, name, period):
        super().__init__(name)
        self.period = period
        self.reset()

    def update(self, kline : Kline):
        if self._last_kline:
            change = kline.close - self._last_kline.close
            gain = max(change, 0)
            loss = abs(min(change, 0))
            self.gains.append(gain)
            self.losses.append(loss)
        else:
            self.gains.append(0)
            self.losses.append(0)

        if len(self.gains) > self.period:
            self.gains.pop(0)
            self.losses.pop(0)

        self._last_value = 0.0

        if len(self.gains) == self.period:
            avg_gain = sum(self.gains) / self.period
            avg_loss = sum(self.losses) / self.period
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs))
            self._last_value = rsi

        self._last_kline = kline

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def reset(self):
        self.gains = []
        self.losses = []
    
    def ready(self):
        return len(self.gains) == self.period