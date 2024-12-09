from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.VolumeProfile import VolumeProfile

class VolumeProfileSignal(Signal):
    def __init__(self, name, symbol, period=100, bins=50, value_area_percentage=70):
        """
        Initialize the Volume Profile Signal.

        :param name: Name of the signal.
        :param symbol: Trading symbol (e.g., 'BTC-USD').
        :param period: Number of recent Klines to include in the Volume Profile.
        :param bins: Number of price bins to divide the price range into.
        :param value_area_percentage: Percentage of total volume to include within the Value Area.
        """
        super().__init__(name, symbol)
        self.period = period
        self.bins = bins
        self.value_area_percentage = value_area_percentage

        # Initialize Volume Profile indicator
        self.volume_profile = VolumeProfile(
            name='volume_profile_indicator',
            period=self.period,
            bins=self.bins,
            value_area_percentage=self.value_area_percentage
        )
        self.reset()

    def reset(self):
        """
        Reset the Volume Profile Signal to its initial state.
        """
        self.volume_profile.reset()
        self._cross_up = False
        self._cross_down = False
        self.previous_close = None

    def update(self, kline: Kline):
        """
        Update the Volume Profile Signal with a new Kline and generate signals.

        :param kline: The new Kline data.
        :return: Signal action ('buy', 'sell', or None).
        """
        vp = self.volume_profile.update(kline)
        if vp is None:
            return None

        poc = vp['poc']
        vah = vp['vah']
        val = vp['val']
        current_price = kline.close

        # Initialize previous_close for first comparison
        if self.previous_close is None:
            self.previous_close = current_price
            return None

        signal_action = None

        # Detect Buy Signal: Price crosses above POC from below and is above VAH
        if self.previous_close <= poc and current_price > poc:
            # Additional confirmation: Price above VAH
            if current_price > vah:
                signal_action = 'buy'

        # Detect Sell Signal: Price crosses below POC from above and is below VAL
        if self.previous_close >= poc and current_price < poc:
            # Additional confirmation: Price below VAL
            if current_price < val:
                signal_action = 'sell'

        # Update previous_close for next iteration
        self.previous_close = current_price

        return signal_action

    def ready(self):
        """
        Check if the Volume Profile Signal is ready to provide trading actions.

        :return: True if ready, False otherwise.
        """
        return self.volume_profile.ready()

    def get_last_value(self):
        """
        Get the latest Volume Profile metrics.

        :return: A dictionary with 'poc', 'vah', 'val', and 'volume_distribution' or None.
        """
        return self.volume_profile.get_last_value()
