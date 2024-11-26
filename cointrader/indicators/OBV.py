from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class OBV(Indicator):
    def __init__(self, name):
        super().__init__(name)
        self.values = []
        self.timestamps = []
        self.klines = []

    def update(self, kline: Kline):
        self.klines.append(kline)
        self.timestamps.append(kline.ts)
        if len(self.values) == 0:
            self.values.append(0)
        else:
            if kline.close > self.klines[-2].close:
                obv_value = self.values[-1] + kline.volume
            elif kline.close < self.klines[-2].close:
                obv_value = self.values[-1] - kline.volume
            else:
                obv_value = self.values[-1]
            self.values.append(obv_value)

        self._last_value = self.values[-1]
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_timestamp(self):
        return self.timestamps[-1]
    
    def get_last_kline(self):
        return self.klines[-1]
    
    def reset(self):
        self.values = []
        self.timestamps = []
        self.klines = []

    def ready(self):
        return len(self.klines) > 1