# This file implements the Volume Oscillator (VO) signal using the VO indicator.
from cointrader.common.Signal import Signal
from cointrader.common.Indicator import Indicator
from cointrader.indicators.VO import VolumeOscillator
from cointrader.common.Kline import Kline
from collections import deque

class VOSignal(Signal):
    def __init__(self, name='vo_signal', symbol=None, short_period=14, long_period=28, threshold=0.0):
        """
        Initialize the Volume Oscillator (VO) signal.
        
        :param short_period: Short-term EMA period.
        :param long_period: Long-term EMA period.
        :param threshold: Signal threshold.
        """
        super().__init__(name, symbol)
        self.vo = VolumeOscillator(short_period=short_period, long_period=long_period)
        self.threshold = threshold
        self._values = deque(maxlen=2)

    def ready(self):
        """
        Check if the VO signal is ready.
        
        :return: True if the signal is ready, False otherwise.
        """
        return self.vo.ready() and len(self._values) == 2

    def reset(self):
        """
        Reset the VO signal to its initial state.
        """
        self.vo.reset()
        self._values.clear()
        self._cross_down = False
        self._cross_up = False

    def update(self, kline: Kline):
        """
        Update the VO signal with a new Kline.
        
        :param kline: The new Kline data.
        :return: The signal value or None if not ready.
        """
        vo_val = self.vo.update(kline)
        if vo_val is None:
            return None
        self._values.append(vo_val)

        # Check for signal cross
        if len(self._values) < 2:
            return None
        
        # Check for signal cross
        if self._values[-1] > self.threshold and self._values[-2] <= self.threshold:
            self._cross_down = False
            self._cross_up = True
        elif self._values[-1] <= -self.threshold and self._values[-2] > -self.threshold:
            self._cross_up = True
            self._cross_down = False

    def cross_up(self):
        return self._cross_up
    
    def cross_down(self):
        return self._cross_down
    
    def increasing(self):
        return self._values[-1] > self._values[-2]
    
    def decreasing(self):
        return self._values[-1] < self._values[-2]
    
    def above(self):
        return self._values[-1] > self.threshold
    
    def below(self):
        return self._values[-1] < -self.threshold
