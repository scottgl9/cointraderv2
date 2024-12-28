# This file implements the Ease of Movement (EOM) indicator
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.SMA import SMA

class EaseOfMovement(Indicator):
    def __init__(self, name='eom', period=14):
        """
        Initialize the Ease of Movement (EOM) indicator with SMA smoothing.
        :param name: Name of the indicator.
        :param sma_period: Period for the SMA smoothing of EOM.
        """
        Indicator.__init__(self, name)
        self.sma = SMA(name=f'{name}_sma', period=period)
        self.previous_kline = None
        self._last_value = 0.0

    def reset(self):
        """
        Reset the EOM indicator.
        """
        self.sma.reset()
        self.previous_kline = None
        self._last_value = 0.0

    def ready(self):
        """
        Check if the EOM is ready for use.
        """
        return self.sma.ready()

    def update(self, kline: Kline):
        """
        Update the EOM indicator with a new Kline.
        :param kline: A Kline object containing high, low, close, and volume data.
        """
        if self.previous_kline is None:
            # Not enough data for the first calculation
            self.previous_kline = kline.copy()
            return 0.0

        # Calculate the midpoint move
        midpoint_current = (kline.high + kline.low) / 2
        midpoint_previous = (self.previous_kline.high + self.previous_kline.low) / 2
        midpoint_move = midpoint_current - midpoint_previous

        # Avoid division by zero for the high-low range
        high_low_range = kline.high - kline.low
        if high_low_range == 0 or kline.volume == 0:
            eom_raw = 0.0
        else:
            # Calculate Ease of Movement (EOM)
            eom_raw = midpoint_move / (kline.volume / high_low_range)

        # Update SMA with the raw EOM value
        self._last_value = self.sma.update_with_value(eom_raw)

        # Store the previous Kline for the next calculation
        self.previous_kline = kline.copy()

        return self._last_value

    def get_last_value(self):
        """
        Get the last calculated EOM value.
        """
        return self._last_value
