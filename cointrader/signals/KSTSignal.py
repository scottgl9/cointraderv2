# This file implements the KST signal, based on the KST (know sure thing) indicator.

from cointrader.common.Signal import Signal
from cointrader.common.Indicator import Indicator
from cointrader.indicators.KST import KST
from cointrader.common.Kline import Kline
from collections import deque

class KSTSignal(Signal):
    def __init__(self, name='kst_signal', symbol=None, roc_periods=[10, 15, 20, 30], smoothing_periods=[10, 10, 10, 15], weights=[1, 2, 3, 4], signal_period=9, threshold=0.0):
        """
        Initialize the Know Sure Thing (KST) signal.
        
        :param roc_periods: List of ROC periods for the four timeframes.
        :param smoothing_periods: List of smoothing periods for the four ROCs.
        :param weights: List of weights for the smoothed ROCs.
        :param signal_period: Signal line EMA period.
        :param threshold: Signal threshold.
        """
        super().__init__(name, symbol)
        self.kst = KST(roc_periods=roc_periods, smoothing_periods=smoothing_periods, weights=weights, signal_period=signal_period)
        self.threshold = threshold
        self._values = deque(maxlen=2)

    def ready(self):
        """
        Check if the KST signal is ready.
        
        :return: True if the signal is ready, False otherwise.
        """
        return self.kst.ready() and len(self._values) == 2

    def reset(self):
        """
        Reset the KST signal to its initial state.
        """
        self.kst.reset()
        self._values.clear()
        self._cross_down = False
        self._cross_up = False

    def update(self, kline: Kline):
        """
        Update the KST signal with a new Kline.
        
        :param kline: The new Kline data.
        :return: The signal value or None if not ready.
        """
        kst_val = self.kst.update(kline)
        if kst_val is None:
            return None
        self._values.append(kst_val)

        # Check for signal cross
        if len(self._values) < 2:
            return None
        
        # Check for signal cross
        if self._values[-1]['kst'] > self._values[-1]['signal'] and self._values[-2]['kst'] <= self._values[-1]['signal']:
            self._cross_up = True
            self._cross_down = False
        elif self._values[-1]['kst'] <= self._values[-1]['signal'] and self._values[-2]['kst'] > self._values[-1]['signal']:
            self._cross_up = False
            self._cross_down = True

    def cross_up(self):
        return self._cross_up
    
    def cross_down(self):
        return self._cross_down
    
    def increasing(self):
        return self._values[-1]['kst'] > self._values[-2]['kst']
    
    def decreasing(self):
        return self._values[-1]['kst'] < self._values[-2]['kst']
    
    def above(self):
        return self._values[-1]['kst'] > self.threshold
    
    def below(self):
        return self._values[-1]['kst'] < self.threshold
