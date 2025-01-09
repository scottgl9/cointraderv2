from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from .ATR import ATR

class ADX(Indicator):
    """
    Average Directional Index (ADX) using simple moving averages (SMA).
    Formula references:

    - upmove = high - high(-1)
    - downmove = low(-1) - low
    - +dm = upmove if upmove > downmove and upmove > 0 else 0
    - -dm = downmove if downmove > upmove and downmove > 0 else 0
    - +di = 100 * (SMA(+dm, period) / ATR(period))
    - -di = 100 * (SMA(-dm, period) / ATR(period))
    - dx = 100 * abs(+di - -di) / (+di + -di)
    - adx = SMA(dx, period)
    """

    def __init__(self, name='adx', period=14):
        super().__init__(name=name)
        self.period = period
        self.atr = ATR(period=self.period)
        self.reset()

    def reset(self):
        # Store the last Kline values so we can compute upmove / downmove
        self.prev_high = None
        self.prev_low = None

        # Rolling windows for +DM, -DM, and DX
        self.plus_dm_window = deque(maxlen=self.period)
        self.minus_dm_window = deque(maxlen=self.period)
        self.dx_window = deque(maxlen=self.period)

        # Latest computed values
        self.plus_di = 0.0
        self.minus_di = 0.0
        self.adx = 0.0

        # Keep references to last output
        self._last_kline = None
        self._last_value = None

    def update(self, kline: Kline):
        """
        Update the ADX with a new Kline (candlestick).
        Returns the latest ADX, or None if not enough data.
        """

        # Update underlying ATR
        self.atr.update(kline)
        if not self.atr.ready():
            # We can't compute ADX until ATR is ready (period bars)
            self._last_kline = kline
            return self._last_value

        cur_high = kline.high
        cur_low = kline.low

        # If we don’t have previous bar info, just store and wait for the next
        if self.prev_high is None or self.prev_low is None:
            self.prev_high = cur_high
            self.prev_low = cur_low
            self._last_kline = kline
            return self._last_value

        # Calculate directional moves
        upmove = cur_high - self.prev_high
        downmove = self.prev_low - cur_low

        # +DM, -DM
        plus_dm = upmove if (upmove > downmove and upmove > 0) else 0.0
        minus_dm = downmove if (downmove > upmove and downmove > 0) else 0.0

        # Add +DM, -DM to rolling windows
        self.plus_dm_window.append(plus_dm)
        self.minus_dm_window.append(minus_dm)

        # Now that we've used these, update previous values
        self.prev_high = cur_high
        self.prev_low = cur_low

        # We can only compute +DI, -DI once we have at least 'period' bars
        if len(self.plus_dm_window) < self.period or not self.atr.ready():
            # Not enough data to produce ADX yet
            self._last_kline = kline
            return self._last_value

        # --- Compute +DI and -DI ---
        # Simple moving average of +DM and -DM
        sum_plus_dm = sum(self.plus_dm_window)
        sum_minus_dm = sum(self.minus_dm_window)

        # ATR for the current bar
        current_atr = self.atr.get_last_value()
        if current_atr == 0:
            # Avoid division by zero
            self._last_kline = kline
            return self._last_value

        self.plus_di = 100.0 * ((sum_plus_dm / self.period) / current_atr)
        self.minus_di = 100.0 * ((sum_minus_dm / self.period) / current_atr)

        # --- Compute DX ---
        di_sum = self.plus_di + self.minus_di
        if di_sum == 0:
            # Avoid division by zero
            self._last_kline = kline
            return self._last_value

        dx = 100.0 * abs(self.plus_di - self.minus_di) / di_sum

        # Add DX to rolling window
        self.dx_window.append(dx)

        # Compute ADX from the simple average of the last 'period' DX values
        if len(self.dx_window) == self.period:
            self.adx = sum(self.dx_window) / self.period

        # Prepare the result dictionary
        self._last_value = {
            'adx': self.adx,
            'pdi': self.plus_di,
            'ndi': self.minus_di
        }
        self._last_kline = kline

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def ready(self):
        """
        Returns True if the indicator has enough data to produce valid ADX.
        """
        return (
            self.atr.ready() and
            len(self.plus_dm_window) == self.period and
            len(self.dx_window) == self.period
        )
