from cointrader.common.Indicator import Indicator

class SMA(Indicator):
    def __init__(self, name, period):
        super().__init__(name)
        self.period = period
        self.values = []
        self.timestamps = []
        self.klines = []

    def update(self, kline):
        self.klines.append(kline)
        self.values.append(kline.close)
        self.timestamps.append(kline.timestamp)
        if len(self.values) > self.period:
            self.values.pop(0)
            self.timestamps.pop(0)
            self.klines.pop(0)
        if len(self.values) == self.period:
            sma_value = sum(self.values) / self.period
            self.values[-1] = sma_value

        return sma_value

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
