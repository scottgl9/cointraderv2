# This file is used to create a signal based on the ADX indicator
from collections import deque
from cointrader.common.Signal import Signal
from cointrader.indicators.ADX import ADX

class ADXSignal(Signal):
    def __init__(self, name='adx', symbol=None, period=14, threshold=25):
        super().__init__(name, symbol)
        self.period = period
        self._threshold = threshold
        self.adx = ADX(period)
        self.reset()

    def reset(self):
        self._values = deque(maxlen=self.period)
        self._cross_up = False
        self._cross_down = False
        self.adx.reset()

    def update(self, kline):
        result = self.adx.update(kline)
        if result is None:
            return
        self._values.append(result)

        if len(self._values) == self.period:
            prev = self._values[-2]
            last = self._values[-1]
            # Cross up: +DI just went above -DI
            if (last['pdi'] > last['ndi']) and (prev['pdi'] <= prev['ndi']):
                self._cross_up = True

            # Cross down: +DI just went below -DI
            if (last['pdi'] < last['ndi']) and (prev['pdi'] >= prev['ndi']):
                self._cross_down = True

    def cross_up(self):
        result = self._cross_up
        self._cross_up = False
        return result

    def cross_down(self):
        result = self._cross_down
        self._cross_down = False
        return result

    def increasing(self):
        if len(self._values) < self.period:
            return False
        return self._values[-1]['adx'] > self._values[-2]['adx']

    def decreasing(self):
        if len(self._values) < self.period:
            return False
        return self._values[-1]['adx'] < self._values[-2]['adx']

    def above(self):
        return self.adx.get_last_value()['adx'] >= self._threshold

    def below(self):
        return self.adx.get_last_value()['adx'] < self._threshold
    
    def ready(self):
        return self.adx.ready()
