# This file contains the MarketProfileSignal class, which is a Signal that uses Market Profile analysis to generate buy/sell signals. *TODO* not working
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.MarketProfile import MarketProfile

class MarketProfileSignal(Signal):
    def __init__(self, name, symbol, period=100, value_area_percentage=70, ib_period=20):
        """
        Initialize the Market Profile Signal.

        :param name: Name of the signal.
        :param symbol: Trading symbol (e.g., 'BTC-USD').
        :param period: Number of recent Klines to include in the Market Profile.
        :param value_area_percentage: Percentage of total TPOs to include within the Value Area.
        :param ib_period: Number of Klines to establish the Initial Balance.
        """
        super().__init__(name, symbol)
        self.period = period
        self.value_area_percentage = value_area_percentage
        self.ib_period = ib_period

        # Initialize Market Profile indicator
        self.market_profile = MarketProfile(
            name='market_profile_indicator',
            period=self.period,
            value_area_percentage=self.value_area_percentage
        )
        self.reset()

    def reset(self):
        """
        Reset the Market Profile Signal to its initial state.
        """
        self.market_profile.reset()
        self.previous_close = None

    def update(self, kline: Kline):
        """
        Update the Market Profile Signal with a new Kline and generate signals.

        :param kline: The new Kline data.
        :return: Signal action ('buy', 'sell', or None).
        """
        vp = self.market_profile.update(kline)
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

        # Detect Buy Signal:
        # 1. Price crosses above POC from below
        # 2. Current price is above VAH
        if self.previous_close <= poc and current_price > poc:
            if current_price > vah:
                signal_action = 'buy'
                self._trigger_alert('Buy Signal', f'Price crossed above POC ({poc:.2f}) and is above VAH ({vah:.2f}).')

        # Detect Sell Signal:
        # 1. Price crosses below POC from above
        # 2. Current price is below VAL
        if self.previous_close >= poc and current_price < poc:
            if current_price < val:
                signal_action = 'sell'
                self._trigger_alert('Sell Signal', f'Price crossed below POC ({poc:.2f}) and is below VAL ({val:.2f}).')

        # Update previous_close for next iteration
        self.previous_close = current_price

        return signal_action

    def ready(self):
        """
        Check if the Market Profile Signal is ready to provide trading actions.

        :return: True if ready, False otherwise.
        """
        return self.market_profile.ready()

    def get_last_value(self):
        """
        Get the latest Market Profile metrics.

        :return: A dictionary with 'poc', 'vah', 'val', and 'profile' or None.
        """
        return self.market_profile.get_last_value()

    def _trigger_alert(self, alert_type, message):
        """
        Trigger an alert for a specific signal.

        :param alert_type: Type of alert ('Buy Signal' or 'Sell Signal').
        :param message: Detailed message for the alert.
        """
        # Example: Print to console (can be integrated with email, SMS, or other notification systems)
        print(f"ALERT - {alert_type}: {message}")
