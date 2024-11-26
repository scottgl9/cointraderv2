from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from .EMA import EMA

class MACD(Indicator):
    def __init__(self, name, short_period, long_period, signal_period):
        super().__init__(name)
        self.short_ema = EMA(f"{name}_short", short_period)
        self.long_ema = EMA(f"{name}_long", long_period)
        self.signal_ema = EMA(f"{name}_signal", signal_period)

    def update(self, kline: Kline):
        short_ema_value = self.short_ema.update(kline)
        long_ema_value = self.long_ema.update(kline)
        macd_value = short_ema_value - long_ema_value

        macd_kline = kline.copy()
        macd_kline.close = macd_value

        signal_value = self.signal_ema.update(macd_kline)
        histogram_value = macd_value - signal_value
        
        self._last_value = {
            "macd": macd_value,
            "signal": signal_value,
            "histogram": histogram_value
        }

        self._last_kline = kline

        return self._last_value

    def get_last_value(self):
        return self._last_value
    
    def get_last_kline(self) -> Kline:
        return self._last_kline

    def reset(self):
        self.short_ema.reset()
        self.long_ema.reset()
        self.signal_ema.reset()
    
    def ready(self):
        return self.short_ema.ready() and self.long_ema.ready() and self.signal_ema.ready()
