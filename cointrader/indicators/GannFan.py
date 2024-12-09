# This file contains the implementation of the Gann Fan indicator.
import math
from collections import deque
from typing import List, Tuple
import matplotlib.pyplot as plt

from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class GannFan(Indicator):
    def __init__(self, name='gann_fan', period=100, angles=None, base_point=None):
        """
        Initialize the Gann Fan indicator.

        :param name: Name of the indicator.
        :param period: Number of recent Klines to consider.
        :param angles: List of Gann angles (in degrees).
        :param base_point: Tuple of (price, time_index) from which to draw the Gann Fan.
        """
        super().__init__(name)
        self.period = period
        self.angles = angles if angles else [45, 26.565, 63.435]  # 1x1, 1x2, 2x1 degrees
        self.base_point = base_point  # (price, time_index)
        self.klines = deque(maxlen=self.period)
        self.gann_lines = {angle: [] for angle in self.angles}
        self.time_index = 0  # Simple counter for time
    
    def reset(self):
        """
        Reset the Gann Fan indicator to its initial state.
        """
        self.klines.clear()
        self.gann_lines = {angle: [] for angle in self.angles}
        self.base_point = None
        self.time_index = 0
    
    def _identify_base_point(self):
        """
        Identify a significant base point (e.g., swing high) from the current Klines.
        For simplicity, we'll choose the highest high in the period as the base point.
        """
        if not self.klines:
            return None
        highest_kline = max(self.klines, key=lambda k: k.high)
        index = self.klines.index(highest_kline)
        return (highest_kline.high, self.time_index - len(self.klines) + index)
    
    def _calculate_gann_lines(self):
        """
        Calculate the Gann Fan lines based on the base point and predefined angles.
        """
        if not self.base_point:
            return
        base_price, base_time = self.base_point
        self.gann_lines = {angle: [] for angle in self.angles}
        for angle in self.angles:
            slope = math.tan(math.radians(angle))
            # For each future time step, calculate the projected price
            for future_time in range(base_time, self.time_index + 1):
                time_diff = future_time - base_time
                projected_price = base_price + slope * time_diff
                self.gann_lines[angle].append((future_time, projected_price))
    
    def update(self, kline: Kline):
        """
        Update the Gann Fan indicator with a new Kline.

        :param kline: The new Kline data.
        :return: Dictionary of Gann lines or None if not ready.
        """
        self.klines.append(kline)
        self.time_index += 1

        # Identify base point if not set or updated
        new_base_point = self._identify_base_point()
        if new_base_point != self.base_point:
            self.base_point = new_base_point
            self._calculate_gann_lines()

        # Update Gann lines with new data
        # For simplicity, append new projected prices based on current Gann lines
        # This can be enhanced to recalculate or adjust angles dynamically
        # Here, we assume static angles and extend the lines
        for angle in self.angles:
            slope = math.tan(math.radians(angle))
            last_time, last_price = self.gann_lines[angle][-1] if self.gann_lines[angle] else self.base_point
            time_diff = self.time_index - last_time
            projected_price = last_price + slope * time_diff
            self.gann_lines[angle].append((self.time_index, projected_price))

        # Prepare the return value
        if self.ready():
            return {
                'gann_lines': self.gann_lines,
                'base_point': self.base_point
            }
        else:
            return None

    def get_last_value(self):
        """
        Get the latest Gann Fan lines and base point.

        :return: Dictionary with 'gann_lines' and 'base_point' or None.
        """
        if self.ready():
            return {
                'gann_lines': self.gann_lines,
                'base_point': self.base_point
            }
        return None

    def ready(self):
        """
        Check if the Gann Fan is ready to provide lines.

        :return: True if ready, False otherwise.
        """
        return len(self.klines) == self.period and self.base_point is not None

    def plot_gann_fan(self):
        """
        Plot the Gann Fan on a price chart.

        Note: This function requires matplotlib and should be called after the indicator is ready.
        """
        if not self.ready():
            print("Gann Fan not ready to plot.")
            return

        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 8))
        prices = [k.close for k in self.klines]
        times = list(range(self.time_index - len(self.klines) + 1, self.time_index + 1))
        plt.plot(times, prices, label='Price', color='black')

        for angle, line in self.gann_lines.items():
            line_times, line_prices = zip(*line)
            plt.plot(line_times, line_prices, label=f'Gann {angle}°')

        base_time, base_price = self.base_point[1], self.base_point[0]
        plt.scatter(base_time, base_price, color='red', label='Base Point')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title('Gann Fan')
        plt.legend()
        plt.grid(True)
        plt.show()
