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
        result = self.macd.update(kline)
        self._macd_values.append(result["macd"])
        self._signal_values.append(result["signal"])
        if len(self._macd_values) > self.window:
            self._macd_values.pop(0)
        if len(self._signal_values) > self.window:
            self._signal_values.pop(0)
        
        if self._macd_values[-1] > max(self._signal_values) and min(self._macd_values) < self._signal_values[-1]:
            self._cross_up = True
        elif self._macd_values[-1] < min(self._signal_values) and max(self._macd_values) > self._signal_values[-1]:
            self._cross_down = True

    def ready(self):
        return self.macd.ready()

    def above(self):
        return self.macd.get_last_value()["macd"] > self.macd.get_last_value()["signal"]
    
    def below(self):
        return self.macd.get_last_value()["macd"] < self.macd.get_last_value()["signal"]

    def cross_up(self):
        result = self._cross_up
        self._cross_up = False
        return result
    
    def cross_down(self):
        result = self._cross_down
        self._cross_down = False
        return result

    def reset(self):
        self.macd.reset()
        self._cross_up = False
        self._cross_down = False
        self._macd_values = []
        self._signal_values = []
