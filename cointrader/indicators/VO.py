# This file implements the Volume Oscillator (VO) indicator
# TODO Implement volume oscillator
from cointrader.common.Kline import Kline
from cointrader.common.Indicator import Indicator
from cointrader.indicators.EMA import EMA

class VolumeOscillator(Indicator):
    def __init__(self, name='vo', short_period=14, long_period=28):
        """
        Initialize the Volume Oscillator (VO) indicator.
        
        :param name: Name of the indicator.
        :param short_period: Short-term EMA period.
        :param long_period: Long-term EMA period.
        """
        super().__init__(name)
        self.short_period = short_period
        self.long_period = long_period

        # Initialize EMA instances for volume
        self.ema_short = EMA(period=self.short_period)
        self.ema_long = EMA(period=self.long_period)

        # Initialize internal state
        self._last_value = None
        self._last_kline = None

    def reset(self):
        """
        Reset the VO indicator to its initial state.
        """
        self.ema_short.reset()
        self.ema_long.reset()
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        """
        Update the VO indicator with a new Kline.
        
        :param kline: The new Kline data.
        :return: The VO value or None if not ready.
        """
        # Update EMAs with the latest volume
        ema_short_val = self.ema_short.update_with_value(kline.volume)
        ema_long_val = self.ema_long.update_with_value(kline.volume)

        # Ensure both EMAs are ready before computing VO
        if not (self.ema_short.ready() and self.ema_long.ready()):
            self._last_kline = kline
            self._last_value = None
            return None

        if ema_long_val == 0:
            # Avoid division by zero
            return None

        # Calculate VO
        vo = ((ema_short_val - ema_long_val) / ema_long_val) * 100.0

        # Store the latest VO value
        self._last_value = vo
        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        """
        Get the latest VO value.
        
        :return: The VO value or None.
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline used to compute VO.
        
        :return: The last Kline object or None.
        """
        return self._last_kline

    def ready(self):
        """
        Check if the VO indicator is ready to provide values.
        
        :return: True if ready, False otherwise.
        """
        return self._last_value is not None
