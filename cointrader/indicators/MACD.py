from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from .EMA import EMA

class MACD(Indicator):
    def __init__(self, name=None, short_period=12, long_period=26, signal_period=9):
        super().__init__(name)
        self.short_ema = EMA(f"{name}_short", short_period)
        self.long_ema = EMA(f"{name}_long", long_period)
        self.signal_ema = EMA(f"{name}_signal", signal_period)

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result

    def update_with_value(self, value: float) -> dict:
        short_ema_value = self.short_ema.update_with_value(value)
        long_ema_value = self.long_ema.update_with_value(value)
        macd_value = short_ema_value - long_ema_value

        signal_value = self.signal_ema.update_with_value(macd_value)
        histogram_value = macd_value - signal_value
        
        self._last_value = {
            "macd": macd_value,
            "signal": signal_value,
            "histogram": histogram_value
        }

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
