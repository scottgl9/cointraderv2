from typing import Dict, List, Tuple
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.GannFan import GannFan

class GannFanSignal(Signal):
    def __init__(self, name, symbol, period=100, angles=None, base_point=None, threshold=0.5):
        """
        Initialize the Gann Fan Signal.

        :param name: Name of the signal.
        :param symbol: Trading symbol.
        :param period: Number of recent Klines to include in the Gann Fan.
        :param angles: List of Gann angles (in degrees).
        :param base_point: Tuple of (price, time_index) from which to draw the Gann Fan.
        :param threshold: Minimum number of Gann lines the price must cross to generate a signal.
        """
        super().__init__(name, symbol)
        self.period = period
        self.angles = angles if angles else [45, 26.565, 63.435]
        self.base_point = base_point
        self.threshold = threshold

        # Initialize Gann Fan indicator
        self.gann_fan = GannFan(
            name='gann_fan_indicator',
            period=self.period,
            angles=self.angles,
            base_point=self.base_point
        )

        # To track previous price position relative to Gann lines
        self.previous_position = {angle: None for angle in self.angles}

    def reset(self):
        """
        Reset the Gann Fan Signal to its initial state.
        """
        self.gann_fan.reset()
        self.previous_position = {angle: None for angle in self.angles}

    def update(self, kline: Kline):
        """
        Update the Gann Fan Signal with a new Kline and generate signals.

        :param kline: The new Kline data.
        :return: Signal action ('buy', 'sell', or None).
        """
        gann_data = self.gann_fan.update(kline)
        if gann_data is None:
            return None

        gann_lines: Dict[float, List[Tuple[int, float]]] = gann_data['gann_lines']
        base_point: Tuple[float, int] = gann_data['base_point']
        current_time = self.gann_fan.time_index
        current_price = kline.close

        crosses_up = 0
        crosses_down = 0

        for angle, line in gann_lines.items():
            # Find the projected price at the current time
            if len(line) < current_time - base_point[1] + 1:
                continue  # Line not extended to current time
            projected_price = line[-1][1]

            # Determine previous position
            prev_pos = self.previous_position[angle]
            if prev_pos is None:
                if current_price > projected_price:
                    self.previous_position[angle] = 'above'
                elif current_price < projected_price:
                    self.previous_position[angle] = 'below'
                else:
                    self.previous_position[angle] = 'on'
                continue

            # Determine current position
            if current_price > projected_price:
                current_pos = 'above'
            elif current_price < projected_price:
                current_pos = 'below'
            else:
                current_pos = 'on'

            # Check for crossover
            if prev_pos == 'below' and current_pos == 'above':
                crosses_up += 1
            elif prev_pos == 'above' and current_pos == 'below':
                crosses_down += 1

            # Update position
            self.previous_position[angle] = current_pos

        # Generate signals based on threshold
        signal_action = None
        if crosses_up >= self.threshold:
            signal_action = 'buy'
            self._trigger_alert('Buy Signal', f"Price crossed above {crosses_up} Gann Fan lines.")
        elif crosses_down >= self.threshold:
            signal_action = 'sell'
            self._trigger_alert('Sell Signal', f"Price crossed below {crosses_down} Gann Fan lines.")

        return signal_action

    def ready(self):
        """
        Check if the Gann Fan Signal is ready to provide trading actions.

        :return: True if ready, False otherwise.
        """
        return self.gann_fan.ready()

    def get_last_value(self):
        """
        Get the latest Gann Fan lines and base point.

        :return: Dictionary with 'gann_lines' and 'base_point' or None.
        """
        return self.gann_fan.get_last_value()

    def _trigger_alert(self, alert_type, message):
        """
        Trigger an alert for a specific signal.

        :param alert_type: Type of alert ('Buy Signal' or 'Sell Signal').
        :param message: Detailed message for the alert.
        """
        # Example: Print to console (can be integrated with email, SMS, or other notification systems)
        print(f"ALERT - {alert_type}: {message}")
