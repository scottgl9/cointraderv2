from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class EMA(Indicator):
    def __init__(self, name, period):
        super().__init__(name)
        self.period = period
        self.values = []
        self.timestamps = []
        self.klines = []
        self.multiplier = 2 / (period + 1)

    def update(self, kline : Kline):
        self.klines.append(kline)
        self.timestamps.append(kline.ts)
        if len(self.values) == 0:
            self.values.append(kline.close)
        else:
            ema_value = (kline.close - self.values[-1]) * self.multiplier + self.values[-1]
            self.values.append(ema_value)
        
        if len(self.values) > self.period:
            self.values.pop(0)
            self.timestamps.pop(0)
            self.klines.pop(0)

        return self.values[-1]

    def get_last_value(self):
        return self.values[-1]
    
    def get_last_timestamp(self):
        return self.timestamps[-1]
    
    def get_last_kline(self):
        return self.klines[-1]
    
    def reset(self):
        self.values = []
        self.timestamps = []
        self.klines = []