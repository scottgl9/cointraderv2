# This file contains the implementation of the Ulcer Index indicator.
from collections import deque
import math
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class UlcerIndex(Indicator):
    def __init__(self, name='ulcer_index', period=14):
        super().__init__(name)
        self.period = period
        self.closes = deque(maxlen=period)
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        # Append the current close
        self.closes.append(kline.close)

        # Only compute when we have enough data
        if len(self.closes) < self.period:
            self._last_kline = kline
            self._last_value = None
            return None

        peak = max(self.closes)
        # Calculate drawdowns for each value in the window
        drawdowns = []
        for c in self.closes:
            dd = ((peak - c) / peak) * 100.0  # Percentage drawdown from peak
            drawdowns.append(dd**2)

        # Average of squared drawdowns
        avg_sq_drawdown = sum(drawdowns) / self.period

        # Ulcer Index is the square root of this average
        ui = math.sqrt(avg_sq_drawdown)

        self._last_kline = kline
        self._last_value = ui
        return ui

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        # Ready when we have at least 'period' bars
        return len(self.closes) == self.period
