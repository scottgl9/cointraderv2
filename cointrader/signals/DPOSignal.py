from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.DPO import DetrendedPriceOscillator

class DPOSignal(Signal):
    def __init__(self, name='dpo', symbol=None, period=20, overbought=50, oversold=-50):
        """
        Initialize the DPO Signal.

        :param name: Name of the signal.
        :param symbol: Trading symbol.
        :param period: Lookback period for DPO.
        :param overbought: Threshold for overbought condition.
        :param oversold: Threshold for oversold condition.
        """
        super().__init__(name, symbol)
        self.dpo = DetrendedPriceOscillator(name='dpo_indicator', period=period)
        self.overbought = overbought
        self.oversold = oversold
        self.reset()

    def reset(self):
        """
        Reset the signal's internal state.
        """
        self.dpo.reset()
        self._cross_up = False
        self._cross_down = False
        self.dpo_values = deque(maxlen=2)  # To track previous and current DPO for cross detection

    def update(self, kline: Kline):
        """
        Update the DPO signal with a new Kline.

        :param kline: New kline data.
        :return: Signal action ('buy', 'sell', or None).
        """
        dpo_val = self.dpo.update(kline)
        if dpo_val is None:
            return None

        self.dpo_values.append(dpo_val)

        # Need at least two DPO values to detect cross
        if len(self.dpo_values) < 2:
            return None

        prev_dpo = self.dpo_values[-2]
        current_dpo = self.dpo_values[-1]

        # Detect bullish signal: DPO crosses above the oversold threshold
        if prev_dpo <= self.oversold and current_dpo > self.oversold:
            self._cross_up = True

        # Detect bearish signal: DPO crosses below the overbought threshold
        if prev_dpo >= self.overbought and current_dpo < self.overbought:
            self._cross_down = True

        signal = None

        if self._cross_up:
            signal = 'buy'
            self._cross_up = False

        if self._cross_down:
            signal = 'sell'
            self._cross_down = False

        return signal
    
    def cross_up(self):
        return self._cross_up
    
    def cross_down(self):
        return self._cross_down

    def ready(self):
        """
        Check if the signal is ready to provide trading actions.

        :return: True if ready, False otherwise.
        """
        return self.dpo.ready()

    def get_last_value(self):
        """
        Get the latest DPO value.

        :return: Latest DPO value or None.
        """
        return self.dpo.get_last_value()
