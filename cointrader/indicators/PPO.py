# This file contains the implementation of the Percentage Price Oscillator (PPO) indicator.
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.EMA import EMA

class PPO(Indicator):
    def __init__(self, name='ppo', short_period=12, long_period=26, signal_period=9):
        """
        Initialize the Percentage Price Oscillator (PPO) indicator.
        
        :param name: Name of the indicator.
        :param short_period: Short-term EMA period.
        :param long_period: Long-term EMA period.
        :param signal_period: Period for the signal line EMA.
        """
        super().__init__(name)
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period

        # Initialize EMA instances
        self.ema_short = EMA(period=self.short_period)
        self.ema_long = EMA(period=self.long_period)
        self.ema_signal = EMA(period=self.signal_period)

        # Initialize internal state
        self._last_value = None
        self._last_kline = None

    def reset(self):
        """
        Reset the PPO indicator to its initial state.
        """
        self.ema_short.reset()
        self.ema_long.reset()
        self.ema_signal.reset()
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        """
        Update the PPO indicator with a new Kline.
        
        :param kline: The new Kline data.
        :return: A dictionary with 'ppo', 'signal', and 'histogram' or None if not ready.
        """
        # Update EMAs with the latest close price
        ema_short_val = self.ema_short.update(kline)
        ema_long_val = self.ema_long.update(kline)

        # Ensure both EMAs are ready before computing PPO
        if not (self.ema_short.ready() and self.ema_long.ready()):
            self._last_kline = kline
            self._last_value = None
            return None

        if ema_long_val == 0:
            # Avoid division by zero
            return None
        # Calculate PPO
        ppo = ((ema_short_val - ema_long_val) / ema_long_val) * 100.0

        # Update the signal line EMA with the PPO value
        signal_val = self.ema_signal.update_with_value(ppo)

        # Ensure the signal line EMA is ready
        if not self.ema_signal.ready():
            self._last_kline = kline
            self._last_value = None
            return None

        # Calculate Histogram
        histogram = ppo - signal_val

        # Store the latest PPO values
        self._last_value = {
            'ppo': ppo,
            'signal': signal_val,
            'histogram': histogram
        }
        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        """
        Get the latest PPO value.
        
        :return: A dictionary with 'ppo', 'signal', and 'histogram' or None.
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline used to compute PPO.
        
        :return: The last Kline object or None.
        """
        return self._last_kline

    def ready(self):
        """
        Check if the PPO indicator is ready to provide values.
        
        :return: True if ready, False otherwise.
        """
        return self._last_value is not None
