# This file implements the Klinger Volume Oscillator (KVO) signal using the KVO indicator.
from cointrader.common.Signal import Signal
from cointrader.common.Indicator import Indicator
from cointrader.indicators.KVO import Klinger
from cointrader.common.Kline import Kline
from collections import deque

class KVOSignal(Signal):
    def __init__(self, name='kvo_signal', symbol=None, short_period=34, long_period=55, signal_period=13, threshold=0.0):
        """
        Initialize the Klinger Volume Oscillator (KVO) signal.
        
        :param short_period: Short-term EMA period.
        :param long_period: Long-term EMA period.
        :param signal_period: Signal line EMA period.
        :param threshold: Signal threshold.
        """
        super().__init__(name, symbol)
        self.kvo = Klinger(short_period, long_period, signal_period)
        self.threshold = threshold
        self._values = deque(maxlen=2)

    def ready(self):
        """
        Check if the KVO signal is ready.
        
        :return: True if the signal is ready, False otherwise.
        """
        return self.kvo.ready() and len(self._values) == 2

    def reset(self):
        """
        Reset the KVO signal to its initial state.
        """
        self.kvo.reset()
        self._values.clear()
        self._cross_down = False
        self._cross_up = False

    def update(self, kline: Kline):
        """
        Update the KVO signal with a new Kline.
        
        :param kline: The new Kline data.
        :return: The signal value or None if not ready.
        """
        result = self.kvo.update(kline)
        if result is None:
            return None
        self._values.append(result)

        # Check for signal cross
        if len(self._values) < 2:
            return None
        
        # Check for signal cross
        if self._values[-1]['kvo'] > self._values[-1]['signal'] and self._values[-2]['kvo'] <= self._values[-1]['signal']:
            self._cross_down = False
            self._cross_up = True
        elif self._values[-1]['kvo'] <= self._values[-1]['signal'] and self._values[-2]['kvo'] > self._values[-1]['signal']:
            self._cross_up = False
            self._cross_down = True

    def cross_up(self):
        return self._cross_up
    
    def cross_down(self):
        return self._cross_down

    def increasing(self):
        return self._values[-1]['kvo'] > self._values[-2]['kvo']
    
    def decreasing(self):
        return self._values[-1]['kvo'] < self._values[-2]['kvo']
    