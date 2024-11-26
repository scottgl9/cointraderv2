from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class ADX(Indicator):
    def __init__(self, name, period):
        super().__init__(name)
        self.period = period
        self.true_range = []
        self.plus_dm = []
        self.minus_dm = []
        self.smooth_tr = []
        self.smooth_plus_dm = []
        self.smooth_minus_dm = []
        self.dx = []
        self.adx = []

    def update(self, kline: Kline):
        if len(self.true_range) == 0:
            self.true_range.append(0)
            self.plus_dm.append(0)
            self.minus_dm.append(0)
        else:
            prev_kline = self.klines[-1]
            tr = max(kline.high - kline.low, abs(kline.high - prev_kline.close), abs(kline.low - prev_kline.close))
            self.true_range.append(tr)
            
            plus_dm = kline.high - prev_kline.high if kline.high - prev_kline.high > prev_kline.low - kline.low else 0
            minus_dm = prev_kline.low - kline.low if prev_kline.low - kline.low > kline.high - prev_kline.high else 0
            self.plus_dm.append(plus_dm)
            self.minus_dm.append(minus_dm)
        
        if len(self.true_range) > self.period:
            self.true_range.pop(0)
            self.plus_dm.pop(0)
            self.minus_dm.pop(0)
        
        if len(self.true_range) == self.period:
            if len(self.smooth_tr) == 0:
                self.smooth_tr.append(sum(self.true_range))
                self.smooth_plus_dm.append(sum(self.plus_dm))
                self.smooth_minus_dm.append(sum(self.minus_dm))
            else:
                self.smooth_tr.append(self.smooth_tr[-1] - (self.smooth_tr[-1] / self.period) + self.true_range[-1])
                self.smooth_plus_dm.append(self.smooth_plus_dm[-1] - (self.smooth_plus_dm[-1] / self.period) + self.plus_dm[-1])
                self.smooth_minus_dm.append(self.smooth_minus_dm[-1] - (self.smooth_minus_dm[-1] / self.period) + self.minus_dm[-1])
            
            tr14 = self.smooth_tr[-1]
            plus_dm14 = self.smooth_plus_dm[-1]
            minus_dm14 = self.smooth_minus_dm[-1]
            
            plus_di14 = 100 * (plus_dm14 / tr14)
            minus_di14 = 100 * (minus_dm14 / tr14)
            
            dx = 100 * abs(plus_di14 - minus_di14) / (plus_di14 + minus_di14)
            self.dx.append(dx)
            
            if len(self.dx) > self.period:
                self.dx.pop(0)
            
            if len(self.dx) == self.period:
                if len(self.adx) == 0:
                    self.adx.append(sum(self.dx) / self.period)
                else:
                    self.adx.append((self.adx[-1] * (self.period - 1) + self.dx[-1]) / self.period)
        
        self.klines.append(kline)
        self._last_value = self.adx[-1] if len(self.adx) > 0 else 0.0
        return self._last_value

    def get_last_value(self):
        return self._last_value
    
    def get_last_timestamp(self):
        return self.klines[-1].ts if len(self.klines) > 0 else 0

    def get_last_kline(self):
        return self.klines[-1] if len(self.klines) > 0 else None
    
    def reset(self):
        self.true_range = []
        self.plus_dm = []
        self.minus_dm = []
        self.smooth_tr = []
        self.smooth_plus_dm = []
        self.smooth_minus_dm = []
        self.dx = []
        self.adx = []
        self.klines = []
        self._ready = False

    def ready(self):
        return len(self.adx) == self.period
