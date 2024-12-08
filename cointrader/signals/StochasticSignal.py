from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.STOCH import StochasticOscillator

class StochasticSignal(Signal):
    def __init__(self, name, symbol, k_period=14, d_period=3, overbought=80, oversold=20):
        super().__init__(name, symbol)
        self.k_period = k_period
        self.d_period = d_period
        self.overbought = overbought
        self.oversold = oversold

        self.stoch = StochasticOscillator(k_period=self.k_period, d_period=self.d_period)
        self.reset()

    def reset(self):
        self.stoch.reset()
        self._cross_up = False
        self._cross_down = False

        self.pk_values = deque(maxlen=2)
        self.pd_values = deque(maxlen=2)

    def update(self, kline: Kline):
        result = self.stoch.update(kline)
        if result is None:
            return None

        pk = result['pk']
        pd = result['pd']

        self.pk_values.append(pk)
        self.pd_values.append(pd)

        # We need at least two data points to detect a cross
        if len(self.pk_values) < 2 or len(self.pd_values) < 2:
            return result

        prev_pk = self.pk_values[-2]
        prev_pd = self.pd_values[-2]

        # Detect cross_up: %K crosses above %D
        # previously pk <= pd and now pk > pd
        # Optionally check oversold condition (pk < self.oversold)
        if prev_pk <= prev_pd and pk > pd:
            # If you want oversold condition, uncomment:
            # if pk < self.oversold:
            self._cross_up = True

        # Detect cross_down: %K crosses below %D
        # previously pk >= pd and now pk < pd
        # Optionally check overbought condition (pk > self.overbought)
        if prev_pk >= prev_pd and pk < pd:
            # If you want overbought condition, uncomment:
            # if pk > self.overbought:
            self._cross_down = True

        return result

    def ready(self):
        return self.stoch.ready()

    def increasing(self):
        # Increasing if %K is rising compared to the previous value
        if len(self.pk_values) < 2:
            return False
        return self.pk_values[-1] > self.pk_values[-2]

    def decreasing(self):
        # Decreasing if %K is falling compared to the previous value
        if len(self.pk_values) < 2:
            return False
        return self.pk_values[-1] < self.pk_values[-2]

    def above(self):
        # %K currently above %D
        if len(self.pk_values) == 0 or len(self.pd_values) == 0:
            return False
        return self.pk_values[-1] > self.pd_values[-1]

    def below(self):
        # %K currently below %D
        if len(self.pk_values) == 0 or len(self.pd_values) == 0:
            return False
        return self.pk_values[-1] < self.pd_values[-1]

    def cross_up(self):
        result = self._cross_up
        self._cross_up = False
        return result

    def cross_down(self):
        result = self._cross_down
        self._cross_down = False
        return result
