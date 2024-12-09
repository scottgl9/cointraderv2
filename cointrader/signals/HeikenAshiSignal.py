from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.HeikinAshi import HeikinAshi
import Optional

class HeikinAshiSignal(Signal):
    def __init__(self, name, symbol, period=100):
        """
        Initialize the Heikin Ashi Signal.

        :param name: Name of the signal.
        :param symbol: Trading symbol.
        :param period: Number of recent Klines to include in the Heikin Ashi.
        """
        super().__init__(name, symbol)
        self.period = period

        # Initialize Heikin Ashi indicator
        self.heikin_ashi = HeikinAshi(name='heikin_ashi_indicator', period=self.period)
        self.reset()

    def reset(self):
        """
        Reset the Heikin Ashi Signal to its initial state.
        """
        self.heikin_ashi.reset()
        self.previous_color: Optional[str] = None  # 'green' or 'red'

    def update(self, kline: Kline) -> Optional[str]:
        """
        Update the Heikin Ashi Signal with a new Kline and generate signals.

        :param kline: The new Kline data.
        :return: Signal action ('buy', 'sell', or None).
        """
        ha_values = self.heikin_ashi.update(kline)
        if ha_values is None:
            return None

        ha_close = ha_values['HA_Close']
        ha_open = ha_values['HA_Open']

        # Determine candle color
        current_color = 'green' if ha_close >= ha_open else 'red'

        signal_action = None

        if self.previous_color:
            if self.previous_color == 'red' and current_color == 'green':
                signal_action = 'buy'
                self._trigger_alert('Buy Signal', 'Heikin Ashi changed from red to green.')
            elif self.previous_color == 'green' and current_color == 'red':
                signal_action = 'sell'
                self._trigger_alert('Sell Signal', 'Heikin Ashi changed from green to red.')

        # Update previous color
        self.previous_color = current_color

        return signal_action

    def ready(self) -> bool:
        """
        Check if the Heikin Ashi Signal is ready to provide trading actions.

        :return: True if ready, False otherwise.
        """
        return self.heikin_ashi.ready()

    def get_last_value(self) -> Optional[Dict[str, float]]:
        """
        Get the latest Heikin Ashi values.

        :return: Dictionary with HA_Open, HA_High, HA_Low, HA_Close or None.
        """
        return self.heikin_ashi.get_last_value()

    def _trigger_alert(self, alert_type: str, message: str):
        """
        Trigger an alert for a specific signal.

        :param alert_type: Type of alert ('Buy Signal' or 'Sell Signal').
        :param message: Detailed message for the alert.
        """
        # Example: Print to console (can be integrated with email, SMS, or other notification systems)
        print(f"ALERT - {alert_type}: {message}")
