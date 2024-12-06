from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.ATR import ATR
import math

class SuperTrend(Indicator):
    def __init__(self, name='supertrend', period=10, multiplier=3.0, atr=None):
        super().__init__(name)
        self.period = period
        self.multiplier = multiplier
        # Use provided ATR or create a new ATR instance if needed
        self.atr = atr if atr is not None else ATR(period=period)

        # Internal state
        self._final_ub = None
        self._final_lb = None
        self._trend_up = True  # Initial guess (same as pandas code)
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        # Update ATR with the current candle
        self.atr.update(kline)

        # If ATR is not ready, we cannot compute supertrend
        if not self.atr.ready():
            self._last_kline = kline
            return self._last_value

        current_close = kline.close
        current_high = kline.high
        current_low = kline.low

        atr_value = self.atr.get_last_value()

        # Basic upper and lower bands
        basic_ub = (current_high + current_low) / 2.0 + self.multiplier * atr_value
        basic_lb = (current_high + current_low) / 2.0 - self.multiplier * atr_value

        # Compute Final Upper Band
        # If we have never set final_ub, initialize it
        if self._final_ub is None:
            # First time we have ATR and can compute supertrend
            final_ub = basic_ub
        else:
            # If close > previous final_ub or previous final_ub == 0 (not applicable since we always have a value)
            # The given code resets final_ub to basic_ub if condition met, else min
            # We'll assume None means the same as 0 for initialization
            if current_close > self._final_ub:
                final_ub = basic_ub
            else:
                final_ub = min(basic_ub, self._final_ub)

        # Compute Final Lower Band
        if self._final_lb is None:
            final_lb = basic_lb
        else:
            if current_close < self._final_lb:
                final_lb = basic_lb
            else:
                final_lb = max(basic_lb, self._final_lb)

        # Determine trend direction
        # According to the pandas code:
        # if close > final_ub[i-1], trend_up = True
        # if close < final_lb[i-1], trend_up = False
        # We must use the previous final_ub/final_lb to decide trend, so if they exist:
        if self._final_ub is not None and self._final_lb is not None:
            # Check previous final_ub and final_lb
            prev_final_ub = self._final_ub
            prev_final_lb = self._final_lb

            if current_close > prev_final_ub:
                self._trend_up = True
            elif current_close < prev_final_lb:
                self._trend_up = False
        else:
            # On very first calculation, trend_up stays as initialized (True)
            # or you can set it based on current_close and final bands.
            # The provided code starts trend_up = True and goes from there.
            pass

        # Supertrend = final_lb if trend_up else final_ub
        if self._trend_up:
            supertrend = final_lb
        else:
            supertrend = final_ub

        # Store values for next iteration
        self._final_ub = final_ub
        self._final_lb = final_lb
        self._last_value = supertrend
        self._last_kline = kline

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def reset(self):
        self.atr.reset()
        self._final_ub = None
        self._final_lb = None
        self._trend_up = True
        self._last_value = None
        self._last_kline = None

    def ready(self):
        return self.atr.ready() and self._last_value is not None
