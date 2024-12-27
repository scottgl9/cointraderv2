from collections import deque
from cointrader.indicators.UO import UltimateOscillator
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline

class UltimateOscillatorSignal(Signal):
    def __init__(self, name='ultimate_oscillator', symbol=None, short_period=7, medium_period=14, long_period=28, overbought=70, oversold=30):
        """
        Initialize the Ultimate Oscillator Signal.
        
        :param name: Name of the signal.
        :param symbol: Trading symbol.
        :param short_period: Short-term period for UO.
        :param medium_period: Medium-term period for UO.
        :param long_period: Long-term period for UO.
        :param overbought: Threshold for overbought condition.
        :param oversold: Threshold for oversold condition.
        """
        super().__init__(name, symbol)
        self.short_period = short_period
        self.medium_period = medium_period
        self.long_period = long_period
        self.overbought = overbought
        self.oversold = oversold
        
        # Initialize Ultimate Oscillator indicator
        self.uo = UltimateOscillator(name='ultimate_oscillator_indicator', short_period=self.short_period, medium_period=self.medium_period, long_period=self.long_period)
        self.uo_values = deque(maxlen=2)  # To track previous and current UO for cross detection
        self.reset()
        
    def reset(self):
        """
        Reset the Ultimate Oscillator Signal to its initial state.
        """
        self.uo.reset()
        self.uo_values.clear()
        self._cross_up = False
        self._cross_down = False

    def ready(self):
        return self.uo.ready() and len(self.uo_values) == 2

    def update(self, kline: Kline):
        """
        Update the Ultimate Oscillator Signal with a new Kline and generate signals.
        
        :param kline: The new Kline data.
        :return: Signal action ('buy', 'sell', or None).
        """
        uo = self.uo.update(kline)
        if uo is None:
            return None
        
        # Append current UO value for crossover detection
        self.uo_values.append(uo)
        
        # Need at least two UO values to detect a cross
        if len(self.uo_values) < 2:
            return None
        
        # Detect cross up
        if self.uo_values[-2] < self.oversold and self.uo_values[-1] >= self.oversold:
            self._cross_up = True
        else:
            self._cross_up = False
        
        # Detect cross down
        if self.uo_values[-2] > self.overbought and self.uo_values[-1] <= self.overbought:
            self._cross_down = True
        else:
            self._cross_down = False
    
    def cross_up(self):
        return self._cross_up
    
    def cross_down(self):
        return self._cross_down
    
    def above(self):
        if not self.ready():
            return False
        return self.uo_values[-1] >= self.overbought
    
    def below(self):
        if not self.ready():
            return False
        return self.uo_values[-1] <= self.oversold

    def increasing(self):
        if not self.ready():
            return False
        return self.uo_values[-1] > self.uo_values[-2]
    
    def decreasing(self):
        if not self.ready():
            return False
        return self.uo_values[-1] < self.uo_values[-2]
    