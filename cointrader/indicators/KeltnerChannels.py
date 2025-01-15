# This file implements Keltner Channels, a volatility indicator that combines the Bollinger Bands and ATR indicators.
from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.ATR import ATR
from cointrader.indicators.SMA import SMA

# def sma(values):
#     """Calculate Simple Moving Average (SMA)."""
#     return sum(values) / len(values) if len(values) > 0 else None

class KeltnerChannels(Indicator):
    def __init__(self, name='keltner_channels', period=20, multiplier=1.5):
        super().__init__(name)
        self.period = period
        self.multiplier = multiplier

        # Price data storage
        self.closes = deque(maxlen=period)

        # ATR indicator instance
        self.atr = ATR(period=period)

        self.sma = SMA(name=f"{name}_sma", period=period)

        # Last calculated values
        self._last_value = None

    def reset(self):
        """Reset the indicator."""
        self.closes.clear()
        self.atr.reset()
        self.sma.reset()
        self._last_value = None

    def ready(self):
        """Check if the indicator is ready to produce output."""
        return len(self.closes) == self.period and self.atr.ready()

    def update(self, kline: Kline):
        """Update the indicator with a new kline."""
        # Update ATR with the current kline
        self.atr.update(kline)

        # Add the new closing price
        self.closes.append(kline.close)

        # Only proceed if we have enough data and ATR is ready
        if len(self.closes) < self.period or not self.atr.ready():
            return None

        middle_line = self.sma.update(kline)

        # Get the current ATR value
        current_atr = self.atr.get_last_value()
        if current_atr is None:
            return None

        # Compute Keltner Channel bounds
        upper_channel = middle_line + self.multiplier * current_atr
        lower_channel = middle_line - self.multiplier * current_atr

        # Save the calculated values
        self._last_value = {
            'middle': middle_line,
            'upper': upper_channel,
            'lower': lower_channel
        }

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        """Return the last calculated values of the Keltner Channels."""
        return self._last_value

    def get_last_kline(self):
        """Return the last processed kline."""
        return self._last_kline

    def ready(self):
        """Check if the indicator is ready to produce output."""
        return self._last_value is not None
