from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class KAMA(Indicator):
    def __init__(self, name='kama', period=10, fast_period=2, slow_period=30):
        super().__init__(name)
        self.period = period
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.values = []
        self.timestamps = []
        self.klines = []
        self._last_value = None

    def update(self, kline: Kline):
        self.klines.append(kline)
        self.values.append(kline.close)
        self.timestamps.append(kline.ts)
        if len(self.values) > self.period:
            self.values.pop(0)
            self.timestamps.pop(0)
            self.klines.pop(0)
        
        if len(self.values) == self.period:
            change = abs(self.values[-1] - self.values[0])
            volatility = sum(abs(self.values[i] - self.values[i - 1]) for i in range(1, self.period))
            er = change / volatility if volatility != 0 else 0
            sc = (er * (2 / (self.fast_period + 1) - 2 / (self.slow_period + 1)) + 2 / (self.slow_period + 1)) ** 2
            
            if self._last_value is None:
                self._last_value = self.values[-1]
            kama_value = self._last_value + sc * (self.values[-1] - self._last_value)
            self._last_value = kama_value

        self._last_kline = kline

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline
    
    def reset(self):
        self.values = []
        self.timestamps = []
        self.klines = []
        self._last_value = None
    
    def ready(self):
        return len(self.values) == self.period