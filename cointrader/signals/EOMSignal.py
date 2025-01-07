# This file implements the Ease of Movement signal, based on the Ease of Movement indicator.

from cointrader.common.Signal import Signal
from cointrader.common.Indicator import Indicator
from cointrader.indicators.EOM import EaseOfMovement
from cointrader.common.Kline import Kline

class EOMSignal(Signal):
    def __init__(self, name='eom_signal', symbol=None, period=14, threshold=0.0):
        """
        Initialize the Ease of Movement (EOM) signal.
        
        :param threshold: Signal threshold.
        """
        super().__init__(name, symbol)
        self._eom = EaseOfMovement(period=period)
        self._threshold = threshold
        self._values = []

    def ready(self):
        """
        Check if the EOM signal is ready.
        
        :return: True if the signal is ready, False otherwise.
        """
        return self._eom.ready() and len(self._values) == 2

    def reset(self):
        """
        Reset the EOM signal to its initial state.
        """
        self._eom.reset()
        self._values.clear()
        self._cross_down = False
        self._cross_up = False

    def update(self, kline: Kline):
        """
        Update the EOM signal with a new Kline.
        
        :param kline: The new Kline data.
        :return: The signal value or None if not ready.
        """
        eom_val = self._eom.update(kline)
        if eom_val is None:
            return None
        self._values.append(eom_val)

        # Check for signal cross
        if len(self._values) < 2:
            return None
        
        # Check for signal cross
        if self._values[-1] > self._threshold and self._values[-2] <= self._threshold:
            self._cross_up = True
        elif self._values[-1] <= self._threshold and self._values[-2] > self._threshold:
            self._cross_down = False
    
    def cross_up(self):
        result = self._cross_up
        self._cross_up = False
        return result
    
    def cross_down(self):
        result = self._cross_down
        self._cross_down = False
        return result
    
    def increasing(self):
        return self._values[-1] > self._values[-2]
    
    def decreasing(self):
        return self._values[-1] < self._values[-2]

    def above(self):
        return self._values[-1] > self._threshold
    
    def below(self):
        return self._values[-1] < self._threshold
