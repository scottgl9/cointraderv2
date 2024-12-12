import math
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class SlopeIndicator(Indicator):
    def __init__(self, slopePeriod=34, slopeInRange=25):
        self.slopePeriod = slopePeriod
        self.slopeInRange = slopeInRange
        self.src_history = []

    def reset(self):
        self.src_history = []

    def update(self, kline: Kline):
        src = kline.close
        self.src_history.append(src)

        # Ensure enough data points for slope calculation
        if len(self.src_history) < self.slopePeriod:
            return None  # Not ready

        # Calculate slope
        slope = self.calculate_slope()
        return {"slope": slope}

    def calculate_slope(self):
        if len(self.src_history) < self.slopePeriod:
            return 0  # Not enough data

        # Use the slopePeriod to define the range for high and low
        highestHigh = max(self.src_history[-self.slopePeriod:])
        lowestLow = min(self.src_history[-self.slopePeriod:])

        # Avoid division by zero
        if highestHigh == lowestLow:
            return 0

        # Calculate slope range
        slope_range = self.slopeInRange / (highestHigh - lowestLow) * lowestLow

        # Use the first and last points in the slopePeriod to compute the slope
        first_value = self.src_history[-self.slopePeriod]
        last_value = self.src_history[-1]

        dt = (last_value - first_value) / first_value * slope_range if first_value != 0 else 0
        c = math.sqrt(1 + dt ** 2)

        # Safe acos input
        acos_input = max(min(1 / c, 1), -1)
        angle = math.degrees(math.acos(acos_input))

        return -angle if dt > 0 else angle

    def ready(self):
        return len(self.src_history) >= self.slopePeriod