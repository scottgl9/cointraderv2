from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class ATR(Indicator):
    def __init__(self, name, period):
        super().__init__(name)
        self.period = period
        self.tr_values = []
        self.atr_values = []
        self.timestamps = []
        self.klines = []

    def update(self, kline: Kline):
        self.klines.append(kline)
        self.timestamps.append(kline.ts)
        
        if len(self.klines) > 1:
            prev_kline = self.klines[-2]
            tr = max(kline.high - kline.low, abs(kline.high - prev_kline.close), abs(kline.low - prev_kline.close))
            self.tr_values.append(tr)
        else:
            self.tr_values.append(kline.high - kline.low)
        
        if len(self.tr_values) >= self.period:
            if len(self.atr_values) == 0:
                self.atr_values.append(sum(self.tr_values[-self.period:]) / self.period)
            else:
                atr = (self.atr_values[-1] * (self.period - 1) + self.tr_values[-1]) / self.period
                self.atr_values.append(atr)
        
        if len(self.tr_values) > self.period:
            self.tr_values.pop(0)
            self.timestamps.pop(0)
            self.klines.pop(0)
        
        return self.atr_values[-1] if self.atr_values else None

    def get_last_value(self):
        return self.atr_values[-1] if self.atr_values else None
    
    def get_last_timestamp(self):
        return self.timestamps[-1] if self.timestamps else None
    
    def get_last_kline(self):
        return self.klines[-1] if self.klines else None
    
    def reset(self):
        self.tr_values = []
        self.atr_values = []
        self.timestamps = []
        self.klines = []