# This is a custom indicator that combines the Bollinger Bands, Keltner Channels, and ATR indicators. Needs to be tested
from collections import deque
import math
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.ATR import ATR
from cointrader.indicators.SMA import SMA

def sma(values):
    return sum(values) / len(values) if len(values) > 0 else None

def stdev(values, mean):
    return math.sqrt(sum((v - mean)**2 for v in values) / len(values)) if len(values) > 1 else 0.0

class SqueezeMomentum(Indicator):
    def __init__(self, name='squeeze_momentum', length=20, multBB=2.0, multKC=1.5):
        super().__init__(name)
        self.length = length
        self.multBB = multBB
        self.multKC = multKC

        # Price data storage
        self.highs = deque(maxlen=length)
        self.lows = deque(maxlen=length)
        self.closes = deque(maxlen=length)
        self.typical_prices = deque(maxlen=length)

        # ATR indicator instance
        self.atr = ATR(period=length)

        self.sma = SMA(name=f"{name}_sma", period=length)

        # For momentum calculation
        self.val_deque = deque(maxlen=length)

        self._last_value = None

    def reset(self):
        self.highs.clear()
        self.lows.clear()
        self.closes.clear()
        self.typical_prices.clear()
        self.atr.reset()
        self.val_deque.clear()
        self.sma.reset()
        self._last_value = None

    def update(self, kline: Kline):
        # Update ATR with the current kline
        self.atr.update(kline)

        # Add the new data points
        self.highs.append(kline.high)
        self.lows.append(kline.low)
        self.closes.append(kline.close)
        tp = (kline.high + kline.low + kline.close) / 3.0
        self.typical_prices.append(tp)

        # Only proceed if we have enough data for Bollinger, Keltner, and ATR
        if len(self.highs) < self.length or not self.atr.ready():
            return None

        # Compute Bollinger Bands
        ma = sma(self.typical_prices)
        sd = stdev(self.typical_prices, ma)
        upperBB = ma + self.multBB * sd
        lowerBB = ma - self.multBB * sd

        # Get ATR value from the ATR indicator
        current_atr = self.atr.get_last_value()
        if current_atr is None:
            return None

        # Compute Keltner Channels
        upperKC = ma + self.multKC * current_atr
        lowerKC = ma - self.multKC * current_atr

        # Squeeze condition: True if Bollinger Bands are inside Keltner Channels
        squeeze_on = (lowerBB > lowerKC) and (upperBB < upperKC)

        # Compute momentum (simplified)
        # Here we simply re-use the MA value as a momentum proxy and compare against its own average
        val = ma
        self.val_deque.append(val)
        hist = val - sma(self.val_deque)

        self._last_value = {
            'squeeze_on': squeeze_on,
            'momentum': hist,
            'upperBB': upperBB,
            'lowerBB': lowerBB,
            'upperKC': upperKC,
            'lowerKC': lowerKC
        }

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        # We consider ourselves ready when we have a last value computed
        return self._last_value is not None
