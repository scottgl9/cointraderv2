# This file implements the Klinger Volume Oscillator (KVO)
# TODO: Check if this implementation is correct
from cointrader.common.Kline import Kline
from cointrader.common.Indicator import Indicator
from cointrader.indicators.EMA import EMA

class Klinger(Indicator):
    def __init__(self, name='klinger', short_period=34, long_period=55, signal_period=13):
        super().__init__(name)
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period

        # Initialize EMAs for short, long, and signal line
        self.short_ema = EMA(name=f'{name}_short_ema', period=short_period)
        self.long_ema = EMA(name=f'{name}_long_ema', period=long_period)
        self.signal_ema = EMA(name=f'{name}_signal_ema', period=signal_period)

        self.reset()

    def reset(self):
        self.short_ema.reset()
        self.long_ema.reset()
        self.signal_ema.reset()
        self._last_kline = None
        self._last_value = None

    def _calculate_rmf(self, kline: Kline, prev_kline: Kline):
        """
        Calculate Raw Money Flow (RMF) for the Klinger Volume Oscillator.
        """
        if not prev_kline or kline.high == kline.low:
            return 0.0

        # Calculate Raw Money Flow (RMF)
        high_low_range = kline.high - kline.low
        midpoint_current = (kline.high + kline.low) / 2
        midpoint_previous = (prev_kline.high + prev_kline.low) / 2

        volume_flow = kline.volume * ((2 * (kline.close - kline.low) - (kline.high - kline.close)) / high_low_range)
        return volume_flow * (midpoint_current - midpoint_previous)

    def update(self, kline: Kline):
        """
        Update the KVO with a new Kline.
        """
        if not self._last_kline:
            # No previous Kline to compare to
            self._last_kline = kline.copy()
            return self._last_value

        # Calculate Raw Money Flow (RMF)
        rmf = self._calculate_rmf(kline, self._last_kline)

        # Update the short and long EMAs with the RMF
        short_ema_value = self.short_ema.update_with_value(rmf)
        long_ema_value = self.long_ema.update_with_value(rmf)

        # Calculate KVO
        kvo_value = short_ema_value - long_ema_value

        # Update the signal line EMA with the KVO value
        signal_line_value = self.signal_ema.update_with_value(kvo_value)

        # Update internal state
        self._last_value = {"kvo": kvo_value, "signal": signal_line_value}
        self._last_kline = kline.copy()

        return self._last_value

    def get_last_value(self):
        """
        Get the last calculated KVO and Signal Line values as a dictionary.
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline used in the calculation.
        """
        return self._last_kline

    def ready(self) -> bool:
        """
        Check if the KVO is ready to provide meaningful results.
        """
        return self.short_ema.ready() and self.long_ema.ready() and self.signal_ema.ready() and self._last_value is not None
