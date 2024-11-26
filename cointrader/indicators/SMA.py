from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class SMA(Indicator):
    def __init__(self, name, period):
        super().__init__(name)
        self.period = period
        self.values = []

    def update(self, kline : Kline):
        self.values.append(kline.close)

        sma_value = kline.close

        if len(self.values) == self.period:
            sma_value = sum(self.values) / self.period
            self.values.append(sma_value)
        
        if len(self.values) > self.period:
            self.values.pop(0)

        self._last_value = sma_value
        self._last_kline = kline
        
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def reset(self):
        self.values = []
    
    def ready(self):
        return len(self.values) == self.period
