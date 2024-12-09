from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.RVI import RelativeVigorIndex

class RVISignal(Signal):
    def __init__(self, name, symbol, period=10, signal_period=4, overbought=70, oversold=30):
        """
        Initialize the RVI Signal.
        
        :param name: Name of the signal.
        :param symbol: Trading symbol.
        :param period: The number of periods for calculating RVI.
        :param signal_period: The number of periods for the signal line SMA.
        :param overbought: Threshold indicating overbought conditions.
        :param oversold: Threshold indicating oversold conditions.
        """
        super().__init__(name, symbol)
        self.period = period
        self.signal_period = signal_period
        self.overbought = overbought
        self.oversold = oversold

        # Initialize RVI indicator
        self.rvi = RelativeVigorIndex(name='rvi_indicator', period=self.period, signal_period=self.signal_period)
        self.reset()

    def reset(self):
        """
        Reset the RVI Signal to its initial state.
        """
        self.rvi.reset()
        self._cross_up = False
        self._cross_down = False
        self.rvi_values = deque(maxlen=2)  # To track previous and current RVI for cross detection

    def update(self, kline: Kline):
        """
        Update the RVI Signal with a new Kline and generate signals.
        
        :param kline: The new Kline data.
        :return: Signal action ('buy', 'sell', or None).
        """
        result = self.rvi.update(kline)
        if result is None:
            return None

        rvi = result['rvi']
        signal = result['signal']
        histogram = result['histogram']

        # Append current RVI value for crossover detection
        self.rvi_values.append(rvi)

        # Need at least two RVI values to detect a cross
        if len(self.rvi_values) < 2:
            return None

        prev_rvi = self.rvi_values[-2]
        current_rvi = self.rvi_values[-1]

        # Detect cross_up: RVI crosses above the signal line
        # Condition: previously RVI <= Signal, now RVI > Signal
        if prev_rvi <= signal and current_rvi > signal:
            self._cross_up = True

        # Detect cross_down: RVI crosses below the signal line
        # Condition: previously RVI >= Signal, now RVI < Signal
        if prev_rvi >= signal and current_rvi < signal:
            self._cross_down = True

        signal_action = None

        if self._cross_up:
            # Optional: Check if RVI is above the oversold threshold for added confirmation
            if rvi > self.oversold:
                signal_action = 'buy'
            self._cross_up = False

        if self._cross_down:
            # Optional: Check if RVI is below the overbought threshold for added confirmation
            if rvi < self.overbought:
                signal_action = 'sell'
            self._cross_down = False

        return signal_action

    def ready(self):
        """
        Check if the RVI Signal is ready to provide trading actions.
        
        :return: True if ready, False otherwise.
        """
        return self.rvi.ready()

    def get_last_value(self):
        """
        Get the latest RVI values.
        
        :return: A dictionary with 'rvi', 'signal', and 'histogram' or None.
        """
        return self.rvi.get_last_value()
