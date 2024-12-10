from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.SuperTrend import SuperTrend

class SupertrendSignal(Signal):
    def __init__(self, name='supertrend', symbol=None, period=14, multiplier=3):
        super().__init__(name, symbol)
        self.period = period
        self.multiplier = multiplier
        self.supertrend = SuperTrend(period=self.period, multiplier=self.multiplier)
        self.reset()

    def reset(self):
        self.supertrend.reset()
        self._trend_up = False
        self._trend_down = False
        self._last_trend_up = False
        self._last_trend_down = False
        self._cross_up = False
        self._cross_down = False

    def update(self, kline: Kline):
        result = self.supertrend.update(kline)
        self._prev_trend_up = self._trend_up
        self._prev_trend_down = self._trend_down

        if self.supertrend.ready():
            self._trend_up = result["trend_up"]
            self._trend_down = result["trend_down"]

        if self._prev_trend_up == False and self._trend_up == True:
            self._cross_up = True
        elif self._prev_trend_down == False and self._trend_down == True:
            self._cross_down = True

    def ready(self):
        return self.supertrend.ready()

    def increasing(self):
        return self._trend_up
    
    def decreasing(self):
        return self._trend_down

    def cross_up(self):
        result = self._cross_up
        self._cross_up = False
        return result

    def cross_down(self):
        result = self._cross_down
        self._cross_down = False
        return result

    def ready(self):
        return self.supertrend.ready()
