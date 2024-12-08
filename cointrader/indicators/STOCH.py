from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.SMA import SMA

class StochasticOscillator(Indicator):
    def __init__(self, name='stochastic', k_period=14, d_period=3):
        super().__init__(name)
        self.k_period = k_period
        self.d_period = d_period

        self.highs = deque(maxlen=k_period)
        self.lows = deque(maxlen=k_period)

        # We'll calculate %K each update and feed it into an SMA for %D
        self.d_sma = SMA(name='stoch_d_sma', period=d_period)

        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        # Add current high and low
        self.highs.append(kline.high)
        self.lows.append(kline.low)

        # Check if we have enough data for %K
        if len(self.highs) < self.k_period:
            # Not enough data yet to produce %K or %D
            self._last_value = None
            self._last_kline = kline
            return None

        highest_high = max(self.highs)
        lowest_low = min(self.lows)

        if highest_high == lowest_low:
            percent_k = 100.0
        else:
            percent_k = ((kline.close - lowest_low) / (highest_high - lowest_low)) * 100.0

        # Update the SMA for %D with the latest %K value
        d_val = self.d_sma.update_with_value(percent_k)

        # Only have a valid %D if the SMA is ready
        if self.d_sma.ready():
            percent_d = self.d_sma.get_last_value()
            self._last_value = {
                'pk': percent_k,
                'pd': percent_d
            }
        else:
            self._last_value = None

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        # Indicator is ready when SMA for %D is ready and we have a last value
        return self._last_value is not None
