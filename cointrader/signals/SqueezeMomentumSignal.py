from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.SqueezeMomentum import SqueezeMomentum
import numpy as np

class SqueezeMomentumSignal(Signal):
    def __init__(self, name='squeeze', symbol=None, length=20, multBB=2.0, multKC=1.5):
        super().__init__(name, symbol)
        self.length = length
        self.multBB = multBB
        self.multKC = multKC
        self.squeeze = SqueezeMomentum(length=self.length, multBB=self.multBB, multKC=self.multKC)
        self.reset()

    def reset(self):
        self.squeeze.reset()
        self._cross_up = False
        self._cross_down = False
        self._prev_squeeze_on = None
        self._momentum_values = deque(maxlen=self.length)

    def update(self, kline: Kline):
        result = self.squeeze.update(kline)
        if result is None:
            return

        squeeze_on = result['squeeze_on']
        momentum = result['momentum']
        self._momentum_values.append(momentum)

        # Initialize previous squeeze state if None
        if self._prev_squeeze_on is None:
            self._prev_squeeze_on = squeeze_on

        # Check for squeeze "firing" event: squeeze just turned OFF
        if self._prev_squeeze_on is True and squeeze_on is False:
            # Squeeze released, check momentum sign for signal
            if momentum > 0:
                # Momentum positive: bullish signal
                self._cross_up = True
            elif momentum < 0:
                # Momentum negative: bearish signal
                self._cross_down = True

        self._prev_squeeze_on = squeeze_on

    def ready(self):
        return self.squeeze.ready()

    def increasing(self):
        # Momentum increasing if last momentum > previous momentum
        if len(self._momentum_values) < 2:
            return False
        return self._momentum_values[-1] > self._momentum_values[-2]

    def decreasing(self):
        if len(self._momentum_values) < 2:
            return False
        return self._momentum_values[-1] < self._momentum_values[-2]

    def above(self):
        # Above zero line
        if len(self._momentum_values) == 0:
            return False
        return self._momentum_values[-1] > 0

    def below(self):
        # Below zero line
        if len(self._momentum_values) == 0:
            return False
        return self._momentum_values[-1] < 0

    def cross_up(self):
        # Returns True if a bullish event (squeeze release with positive momentum) happened
        result = self._cross_up
        self._cross_up = False
        return result

    def cross_down(self):
        # Returns True if a bearish event (squeeze release with negative momentum) happened
        result = self._cross_down
        self._cross_down = False
        return result
