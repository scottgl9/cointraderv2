from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class IchimokuCloud(Indicator):
    def __init__(self, name, short_period=9, medium_period=26, long_period=52):
        super().__init__(name)
        self.short_period = short_period
        self.medium_period = medium_period
        self.long_period = long_period
        self.tenkan_sen = []
        self.kijun_sen = []
        self.senkou_span_a = []
        self.senkou_span_b = []
        self.chikou_span = []
        self.klines = []

    def update(self, kline: Kline):
        self.klines.append(kline)
        if len(self.klines) > self.long_period:
            self.klines.pop(0)

        if len(self.klines) >= self.short_period:
            high = max(k.high for k in self.klines[-self.short_period:])
            low = min(k.low for k in self.klines[-self.short_period:])
            self.tenkan_sen.append((high + low) / 2)
        else:
            self.tenkan_sen.append(None)

        if len(self.klines) >= self.medium_period:
            high = max(k.high for k in self.klines[-self.medium_period:])
            low = min(k.low for k in self.klines[-self.medium_period:])
            self.kijun_sen.append((high + low) / 2)
        else:
            self.kijun_sen.append(None)

        if len(self.tenkan_sen) > 1 and len(self.kijun_sen) > 1:
            self.senkou_span_a.append((self.tenkan_sen[-2] + self.kijun_sen[-2]) / 2)
        else:
            self.senkou_span_a.append(None)

        if len(self.klines) >= self.long_period:
            high = max(k.high for k in self.klines[-self.long_period:])
            low = min(k.low for k in self.klines[-self.long_period:])
            self.senkou_span_b.append((high + low) / 2)
        else:
            self.senkou_span_b.append(None)

        self.chikou_span.append(kline.close)
        self._last_kline = kline

        self._last_value = {
            'tenkan_sen': self.tenkan_sen[-1],
            'kijun_sen': self.kijun_sen[-1],
            'senkou_span_a': self.senkou_span_a[-1],
            'senkou_span_b': self.senkou_span_b[-1],
            'chikou_span': self.chikou_span[-1]
        }

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def reset(self):
        self.tenkan_sen = []
        self.kijun_sen = []
        self.senkou_span_a = []
        self.senkou_span_b = []
        self.chikou_span = []
        self.klines = []

    def ready(self):
        return len(self.klines) >= self.long_period