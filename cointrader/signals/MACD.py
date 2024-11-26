from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.MACD import MACD

class MACDSignal(Signal):
    def __init__(self, name, symbol, short_period, long_period, signal_period):
        super().__init__(name, symbol)
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period
        self.window = max(short_period, long_period, signal_period)
        self.macd = MACD(short_period=self.short_period,
                         long_period=self.long_period,
                         signal_period=self.signal_period)
        self.reset()

    def update(self, kline: Kline):
        self._values.append(self.macd.update(kline))
        if len(self._values) > self.window:
            self._values.pop(0)

    def ready(self):
        return self.macd.ready()

    def cross_up(self):
        return self.macd.get_last_value()["macd"] > self.macd.get_last_value()["signal"]
    
    def cross_down(self):
        return self.macd.get_last_value()["macd"] < self.macd.get_last_value()["signal"]

    def get_last_value(self):
        return {
            "macd": self.macd,
            "signal": self.signal,
            "histogram": self.histogram
        }

    def reset(self):
        self.macd.reset()
        self._cross_up = False
        self._cross_down = False
