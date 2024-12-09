from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.CMF import ChaikinMoneyFlow

class CMFSignal(Signal):
    def __init__(self, name, symbol, period=20, signal_period=9, overbought=0.05, oversold=-0.05):
        """
        Initialize the CMF Signal.

        :param name: Name of the signal.
        :param symbol: Trading symbol.
        :param period: Number of periods for CMF calculation.
        :param signal_period: Number of periods for the CMF signal line.
        :param overbought: Threshold indicating overbought conditions.
        :param oversold: Threshold indicating oversold conditions.
        """
        super().__init__(name, symbol)
        self.period = period
        self.signal_period = signal_period
        self.overbought = overbought
        self.oversold = oversold

        # Initialize CMF indicator
        self.cmf = ChaikinMoneyFlow(name='chaikin_money_flow_indicator', period=self.period)

        # Initialize Signal Line SMA
        self.signal_sma = SimpleMovingAverage(name='cmf_signal_sma', period=self.signal_period)

        # Initialize deque to track CMF values for cross detection
        self.cmf_values = deque(maxlen=2)

        # Internal flags
        self._cross_up = False
        self._cross_down = False

    def reset(self):
        """
        Reset the CMF Signal to its initial state.
        """
        self.cmf.reset()
        self.signal_sma.reset()
        self.cmf_values.clear()
        self._cross_up = False
        self._cross_down = False

    def update(self, kline: Kline):
        """
        Update the CMF Signal with a new Kline and generate signals.

        :param kline: The new Kline data.
        :return: Signal action ('buy', 'sell', or None).
        """
        cmf_val = self.cmf.update(kline)
        if cmf_val is not None:
            signal_line = self.signal_sma.update_with_value(cmf_val)
            if signal_line is not None:
                # Append current CMF value for crossover detection
                self.cmf_values.append(cmf_val)

                if len(self.cmf_values) < 2:
                    return None

                prev_cmf, current_cmf = list(self.cmf_values)

                # Detect cross_up: CMF crosses above Signal Line
                if prev_cmf <= signal_line and current_cmf > signal_line:
                    self._cross_up = True

                # Detect cross_down: CMF crosses below Signal Line
                if prev_cmf >= signal_line and current_cmf < signal_line:
                    self._cross_down = True

                signal_action = None

                if self._cross_up:
                    # Optional: Check if CMF is above oversold threshold for added confirmation
                    if current_cmf > self.oversold:
                        signal_action = 'buy'
                    self._cross_up = False

                if self._cross_down:
                    # Optional: Check if CMF is below overbought threshold for added confirmation
                    if current_cmf < self.overbought:
                        signal_action = 'sell'
                    self._cross_down = False

                return signal_action

        return None

    def ready(self):
        """
        Check if the CMF Signal is ready to provide trading actions.

        :return: True if ready, False otherwise.
        """
        return self.cmf.ready() and len(self.cmf_values) == 2 and self.signal_sma.ready()

    def get_last_value(self):
        """
        Get the latest CMF and Signal Line values.

        :return: A dictionary with 'cmf' and 'signal_line' or None.
        """
        if self.cmf.ready() and self.signal_sma.ready():
            return {
                'cmf': self.cmf.get_last_value(),
                'signal_line': self.signal_sma.get_last_value()
            }
        return None

# SimpleMovingAverage Helper Class
class SimpleMovingAverage:
    """Simple Moving Average (SMA) calculator."""
    def __init__(self, name='sma', period=9):
        """
        Initialize the SMA calculator.

        :param name: Name of the SMA indicator.
        :param period: The number of periods over which to calculate the SMA.
        """
        self.name = name
        self.period = period
        self.values = deque(maxlen=period)
        self.sum = 0.0
        self.current_sma = None

    def update_with_value(self, new_value):
        """
        Update the SMA with a new value.

        :param new_value: The new data point (float).
        :return: The updated SMA value or None if not enough data.
        """
        if len(self.values) == self.period:
            # Remove the oldest value from the sum
            oldest = self.values.popleft()
            self.sum -= oldest

        # Add the new value
        self.values.append(new_value)
        self.sum += new_value

        if len(self.values) == self.period:
            self.current_sma = self.sum / self.period
            return self.current_sma
        else:
            self.current_sma = None
            return None

    def get_last_value(self):
        """
        Get the current SMA value.

        :return: The latest SMA value or None.
        """
        return self.current_sma

    def ready(self):
        """
        Check if the SMA is ready (i.e., has received enough data).

        :return: True if ready, False otherwise.
        """
        return len(self.values) == self.period

    def reset(self):
        """
        Reset the SMA calculator to its initial state.
        """
        self.values.clear()
        self.sum = 0.0
        self.current_sma = None
