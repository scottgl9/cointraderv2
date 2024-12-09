# This file contains the implementation of the Percentage Volume Oscillator (PVO) indicator.
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.EMA import EMA

class PVO(Indicator):
    def __init__(self, name='pvo', short_period=12, long_period=26, signal_period=9):
        super().__init__(name)
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period

        self.ema_short = EMA(self.short_period)
        self.ema_long = EMA(self.long_period)
        self.ema_signal = EMA(self.signal_period)

        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        volume = kline.volume
        short_ema_val = self.ema_short.update_with_value(volume)
        short_ema_val = self.ema_short.update_with_value(volume)
        long_ema_val = self.ema_long.update_with_value(volume)
        # We can only compute PVO once both EMAs are ready
        if not (self.ema_short.ready() and self.ema_long.ready()):
            self._last_kline = kline
            return None

        if long_ema_val == 0:
            # Avoid division by zero, if there's no volume this would be unusual,
            # but just return None in that scenario.
            self._last_kline = kline
            self._last_value = None
            return None

        pvo = ((short_ema_val - long_ema_val) / long_ema_val) * 100.0

        # Compute signal line if possible
        signal_val = self.ema_signal.update_with_value(pvo)

        if not self.ema_signal.ready():
            self._last_kline = kline
            self._last_value = None
            return None

        # Once we have the PVO and signal, we can also compute histogram
        histogram = pvo - signal_val

        self._last_value = {
            'pvo': pvo,
            'signal': signal_val,
            'histogram': histogram
        }
        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        # Ready when the signal line EMA is ready, meaning we have pvo, signal
        return self._last_value is not None
