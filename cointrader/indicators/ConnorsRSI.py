# This implements the Connors RSI indicator, which is a composite indicator that combines the RSI, a streak RSI, and a one-day ROC RSI. 
# The Connors RSI is computed as the average of the three RSIs. The Connors RSI is used to identify overbought and oversold conditions in a security.
from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.RSI import RSI
from cointrader.indicators.ROC import ROC


class ConnorsRSI(Indicator):
    def __init__(self, name='connors_rsi', rsi_length=3, streak_rsi_length=2, roc_rsi_length=100):
        super().__init__(name)
        self.rsi_length = rsi_length
        self.streak_rsi_length = streak_rsi_length
        self.roc_rsi_length = roc_rsi_length

        self.closes = deque()
        self.streak = 0

        # Instantiate RSI indicators
        self.price_rsi = RSI(period=self.rsi_length)
        self.streak_rsi = RSI(period=self.streak_rsi_length)
        # ROC for 1-day change: Use period=2, so that after the second bar, we have a one-bar ROC.
        self.roc = ROC(period=2)
        self.roc_rsi = RSI(period=self.roc_rsi_length)

        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        close = kline.close
        self.closes.append(close)

        # Update Price RSI with the current close
        price_rsi_val = self.price_rsi.update_with_value(close)

        # Compute/update streak:
        if len(self.closes) > 1:
            prev_close = self.closes[-2]
            if close > prev_close:
                self.streak = self.streak + 1 if self.streak >= 0 else 1
            elif close < prev_close:
                self.streak = self.streak - 1 if self.streak <= 0 else -1
            else:
                self.streak = 0

        # Update Streak RSI with the streak value
        # Convert streak to float to keep it consistent
        streak_rsi_val = self.streak_rsi.update_with_value(float(self.streak))

        # Update ROC with the current kline
        roc_val = self.roc.update(kline)

        # If ROC is ready, update ROC RSI with its value
        if roc_val is not None:
            roc_rsi_val = self.roc_rsi.update_with_value(roc_val)
        else:
            roc_rsi_val = None

        # Only compute Connors RSI if all three RSIs are ready and have values
        # Check that each RSI is ready and the values are not None
        if (self.price_rsi.ready() and price_rsi_val is not None and
            self.streak_rsi.ready() and streak_rsi_val is not None and
            self.roc.ready() and self.roc_rsi.ready() and roc_rsi_val is not None):

            connors_rsi_val = (price_rsi_val + streak_rsi_val + roc_rsi_val) / 3.0
            self._last_value = connors_rsi_val
        else:
            self._last_value = None

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        return self._last_value is not None
