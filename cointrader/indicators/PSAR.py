from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class PSAR(Indicator):
    def __init__(self, name, af=0.02, max_af=0.2):
        super().__init__(name)
        self.af = af
        self.max_af = max_af
        self.ep = None
        self.psar = None
        self.trend = None
        self.af_increment = af
        self.klines = []

    def update(self, kline: Kline):
        self.klines.append(kline)
        if len(self.klines) < 2:
            self.psar = kline.low
            self.ep = kline.high
            self.trend = 1
            return self.psar

        prev_kline = self.klines[-2]
        if self.trend == 1:
            self.psar = self.psar + self.af * (self.ep - self.psar)
            if kline.low < self.psar:
                self.trend = -1
                self.psar = self.ep
                self.ep = kline.low
                self.af = self.af_increment
            else:
                if kline.high > self.ep:
                    self.ep = kline.high
                    self.af = min(self.af + self.af_increment, self.max_af)
        else:
            self.psar = self.psar + self.af * (self.ep - self.psar)
            if kline.high > self.psar:
                self.trend = 1
                self.psar = self.ep
                self.ep = kline.high
                self.af = self.af_increment
            else:
                if kline.low < self.ep:
                    self.ep = kline.low
                    self.af = min(self.af + self.af_increment, self.max_af)

        self._last_kline = kline

        return self.psar

    def get_last_value(self):
        return self.psar

    def get_last_timestamp(self):
        return self._last_kline.ts

    def get_last_kline(self):
        return self._last_kline

    def reset(self):
        self.af = self.af_increment
        self.ep = None
        self.psar = None
        self.trend = None
        self.klines = []

    def ready(self):
        return len(self.klines) > 1