from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from .EMA import EMA

class MACD(Indicator):
    def __init__(self, name, short_period, long_period, signal_period):
        super().__init__(name)
        self.short_ema = EMA(f"{name}_short", short_period)
        self.long_ema = EMA(f"{name}_long", long_period)
        self.signal_ema = EMA(f"{name}_signal", signal_period)
        self.macd_values = []
        self.signal_values = []
        self.histogram_values = []

    def update(self, kline: Kline):
        short_ema_value = self.short_ema.update(kline)
        long_ema_value = self.long_ema.update(kline)
        macd_value = short_ema_value - long_ema_value
        self.macd_values.append(macd_value)
        
        signal_value = self.signal_ema.update(Kline(kline.ts, macd_value, macd_value, macd_value, macd_value, 0))
        self.signal_values.append(signal_value)
        
        histogram_value = macd_value - signal_value
        self.histogram_values.append(histogram_value)
        
        if len(self.macd_values) > self.signal_ema.period:
            self.macd_values.pop(0)
            self.signal_values.pop(0)
            self.histogram_values.pop(0)

        return macd_value, signal_value, histogram_value

    def get_last_value(self):
        return self.macd_values[-1], self.signal_values[-1], self.histogram_values[-1]

    def reset(self):
        self.short_ema.reset()
        self.long_ema.reset()
        self.signal_ema.reset()
        self.macd_values = []
        self.signal_values = []
        self.histogram_values = []