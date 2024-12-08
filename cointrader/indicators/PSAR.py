from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class PSAR(Indicator):
    def __init__(self, name='psar', af=0.02, max_af=0.2):
        super().__init__(name)
        self.af_increment = af
        self.max_af = max_af
        self.reset()

    def reset(self):
        self.af = self.af_increment
        self.ep = None
        self.psar = None
        self.trend = None
        self.klines = []
        self._last_kline = None
        self._last_value = None

    def update(self, kline: Kline):
        self.klines.append(kline)

        # Initialization for the first bar
        if self._last_kline is None:
            # Assume an initial uptrend and use the first bar's low/high as starting points
            self.psar = kline.low
            self.ep = kline.high
            self.trend = 1
            self._last_kline = kline
            self._last_value = self.psar
            return self.psar

        prev_psar = self.psar
        prev_ep = self.ep
        prev_af = self.af
        prev_trend = self.trend

        # Calculate the new PSAR value (raw, before clamping or checking reversal)
        self.psar = prev_psar + prev_af * (prev_ep - prev_psar)

        # Check for trend reversal first:
        # Uptrend reversing to downtrend if current low < new PSAR
        # Downtrend reversing to uptrend if current high > new PSAR
        reversed_trend = False
        if prev_trend == 1:
            # Currently in uptrend, check if we should go down
            if kline.low < self.psar:
                # Reversal to downtrend
                self.trend = -1
                self.psar = prev_ep  # set PSAR to previous EP
                self.ep = kline.low  # new EP is current low
                self.af = self.af_increment
                reversed_trend = True
            else:
                # No reversal, just continue uptrend logic
                if kline.high > prev_ep:
                    self.ep = kline.high
                    self.af = min(prev_af + self.af_increment, self.max_af)
                else:
                    self.ep = prev_ep
                    self.af = prev_af
        else:
            # Currently in downtrend, check if we should go up
            if kline.high > self.psar:
                # Reversal to uptrend
                self.trend = 1
                self.psar = prev_ep  # set PSAR to previous EP
                self.ep = kline.high  # new EP is current high
                self.af = self.af_increment
                reversed_trend = True
            else:
                # No reversal, just continue downtrend logic
                if kline.low < prev_ep:
                    self.ep = kline.low
                    self.af = min(prev_af + self.af_increment, self.max_af)
                else:
                    self.ep = prev_ep
                    self.af = prev_af

        # If not reversed, clamp the PSAR based on the last two bars
        if not reversed_trend:
            if len(self.klines) >= 2:
                last_low = self.klines[-1].low
                second_last_low = self.klines[-2].low
                last_high = self.klines[-1].high
                second_last_high = self.klines[-2].high
            else:
                last_low = self.klines[-1].low
                second_last_low = last_low
                last_high = self.klines[-1].high
                second_last_high = last_high

            if self.trend == 1:
                # Uptrend: PSAR cannot be greater than the lowest of the last two lows
                self.psar = min(self.psar, last_low, second_last_low)
            else:
                # Downtrend: PSAR cannot be less than the highest of the last two highs
                self.psar = max(self.psar, last_high, second_last_high)

        self._last_kline = kline
        self._last_value = self.psar
        return self.psar

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        return len(self.klines) > 1
