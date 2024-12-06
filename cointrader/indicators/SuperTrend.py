from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.ATR import ATR
import math

class SuperTrend(Indicator):
    def __init__(self, name='supertrend', period=10, multiplier=3.0):
        super().__init__(name)
        self.period = period
        self.multiplier = multiplier
        self.atr = ATR(period=period)
        self.reset()

    def update(self, kline: Kline):
        # Update ATR with the current candle
        self.atr.update(kline)

        # If ATR not ready, we cannot compute SuperTrend yet
        if not self.atr.ready():
            self._last_kline = kline
            return self._last_value

        current_close = kline.close
        current_high = kline.high
        current_low = kline.low

        atr_value = self.atr.get_last_value()

        # Compute basic upper and lower bands
        basic_ub = (current_high + current_low) / 2.0 + (self.multiplier * atr_value)
        basic_lb = (current_high + current_low) / 2.0 - (self.multiplier * atr_value)

        # Treat previous final_ub and final_lb as zero if we don't have them yet
        prev_final_ub = self._final_ub if self._final_ub is not None else 0.0
        prev_final_lb = self._final_lb if self._final_lb is not None else 0.0

        # Compute the new final_ub for this candle
        # If Close > prev_final_ub or prev_final_ub == 0 => final_ub = basic_ub
        # else final_ub = min(basic_ub, prev_final_ub)
        if current_close > prev_final_ub or prev_final_ub == 0.0:
            final_ub = basic_ub
        else:
            final_ub = min(basic_ub, prev_final_ub)

        # Compute the new final_lb for this candle
        # If Close < prev_final_lb or prev_final_lb == 0 => final_lb = basic_lb
        # else final_lb = max(basic_lb, prev_final_lb)
        if current_close < prev_final_lb or prev_final_lb == 0.0:
            final_lb = basic_lb
        else:
            final_lb = max(basic_lb, prev_final_lb)

        # Determine trend direction based on previous final_ub and final_lb
        # If Close > prev_final_ub => trend_up = True
        # If Close < prev_final_lb => trend_up = False
        # Otherwise, trend_up remains unchanged
        if current_close > prev_final_ub:
            self._trend_up = True
            self._trend_down = False
        elif current_close < prev_final_lb:
            self._trend_up = False
            self._trend_down = True

        # If none of the conditions met, trend_up stays as is

        # Now assign the supertrend value for this candle
        # trend_up => supertrend = final_lb
        # trend_down => supertrend = final_ub
        supertrend = final_lb if self._trend_up else final_ub

        # Store values for next iteration
        self._final_ub = final_ub
        self._final_lb = final_lb
        self._last_value = {
            'supertrend': supertrend,
            'trend_up': self._trend_up,
            'trend_down': self._trend_down
        }
        self._last_kline = kline

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def reset(self):
        self.atr.reset()
        # Initialize final_ub and final_lb to None, will treat them as 0.0 when None
        self._final_ub = None
        self._final_lb = None
        self._trend_up = False
        self._trend_down = False
        self._last_value = None
        self._last_kline = None

    def ready(self):
        return self.atr.ready() and self._last_value is not None
