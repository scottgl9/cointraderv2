import math
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class SlopeAdaptiveMovingAverage(Indicator):
    def __init__(self, length=200, majLength=14, minLength=6, slopePeriod=34, slopeInRange=25, flat=17):
        self.length = length
        self.majLength = majLength
        self.minLength = minLength
        self.slopePeriod = slopePeriod
        self.slopeInRange = slopeInRange
        self.flat = flat

        self.minAlpha = 2 / (self.minLength + 1)
        self.majAlpha = 2 / (self.majLength + 1)

        self.reset()

    def reset(self):
        self.src_history = []
        self.ma = None
        self.swing = 0
        self.ma_history = []
        self.slope_history = []

    def update(self, kline: Kline):
        src = kline.close
        self.src_history.append(src)

        # Ensure enough data points for calculation
        if len(self.src_history) < self.length + 1:
            return None  # Not ready

        # Calculate highest high and lowest low
        hh = max(self.src_history[-(self.length + 1):])
        ll = min(self.src_history[-(self.length + 1):])

        # Calculate the multiplier
        mult = abs(2 * src - ll - hh) / (hh - ll) if hh != ll else 0

        # Final alpha value
        final_alpha = mult * (self.minAlpha - self.majAlpha) + self.majAlpha

        # Calculate moving average
        if self.ma is None:
            self.ma = src  # Initialize with the first value
        else:
            self.ma += (final_alpha ** 2) * (src - self.ma)
        self.ma_history.append(self.ma)

        # Calculate the slope
        slope = self.calculate_slope()
        self.slope_history.append(slope)

        # Determine trend directions
        up = slope >= self.flat
        down = slope <= -self.flat

        # Generate buy/sell signals
        prev_swing = self.swing
        if up and self.swing <= 0:
            self.swing = 1  # Long signal
        elif down and self.swing >= 0:
            self.swing = -1  # Short signal

        longsignal = self.swing == 1 and prev_swing != 1
        shortsignal = self.swing == -1 and prev_swing != -1

        return {
            "ma": self.ma,
            "slope": slope,
            "longsignal": longsignal,
            "shortsignal": shortsignal,
        }

    def calculate_slope(self):
        if len(self.ma_history) < self.slopePeriod:
            return 0  # Not enough data

        # Get historical data for slope calculation
        ma = self.ma_history[-1]
        ma_2 = self.ma_history[-3]  # Value from two periods ago

        highestHigh = max(self.src_history[-self.slopePeriod:])
        lowestLow = min(self.src_history[-self.slopePeriod:])

        # Avoid division by zero
        if highestHigh == lowestLow:
            return 0

        # Calculate slope range
        slope_range = self.slopeInRange / (highestHigh - lowestLow) * lowestLow

        # Calculate the slope angle
        dt = (ma_2 - ma) / ma * slope_range if ma != 0 else 0
        c = math.sqrt(1 + dt ** 2)

        # Safe acos input
        acos_input = max(min(1 / c, 1), -1)
        angle = math.degrees(math.acos(acos_input))

        return -angle if dt > 0 else angle

    def ready(self):
        return len(self.src_history) >= self.length + 1
