# This file contains the implementation of the Klinger Volume Oscillator (KVO) indicator.
from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.VWAP import VWAP
from cointrader.indicators.EMA import EMA

class Klinger(Indicator):
    def __init__(self, name='klinger', short_period=34, long_period=55, signal_period=13):
        """
        Initialize the Klinger Volume Oscillator (KVO) indicator.

        :param name: Name of the indicator.
        :param short_period: Number of periods for the short EMA.
        :param long_period: Number of periods for the long EMA.
        :param signal_period: Number of periods for the signal line EMA.
        """
        super().__init__(name)
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period

        # Initialize the VWAP and EMA indicators
        self.vwap = VWAP()
        self.short_ema = EMA(period=short_period)
        self.long_ema = EMA(period=long_period)
        self.signal_ema = EMA(period=signal_period)

        # Internal state
        self.reset()

    def reset(self):
        """
        Reset the KVO indicator to its initial state.
        """
        self.vwap.reset()
        self.short_ema.reset()
        self.long_ema.reset()
        self.signal_ema.reset()
        self._last_kline = None
        self._last_value = None

    def update(self, kline: Kline):
        """
        Update the KVO indicator with a new Kline.

        :param kline: The new Kline data.
        :return: The updated KVO value or None if not enough data.
        """
        vwap = self.vwap.update(kline)
        if vwap is None:
            return self._last_value

        short_ema = self.short_ema.update_with_value(vwap)
        long_ema = self.long_ema.update_with_value(vwap)
        if short_ema is None or long_ema is None:
            return self._last_value

        kvo = short_ema - long_ema
        signal = self.signal_ema.update_with_value(kvo)
        if signal is None:
            return self._last_value

        self._last_kline = kline.copy()
        self._last_value = {'kvo': kvo, 'signal': signal}

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline
    
    def ready(self):
        return self._last_value is not None
