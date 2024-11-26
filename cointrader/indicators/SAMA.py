import math
from cointrader.common.Indicator import Indicator

class SlopeAdaptiveMovingAverage(Indicator):
    def __init__(self, length=200, majLength=14, minLength=6, slopePeriod=34, slopeInRange=25, flat=17):
        # Initialize parameters
        self.length = length
        self.majLength = majLength
        self.minLength = minLength
        self.slopePeriod = slopePeriod
        self.slopeInRange = slopeInRange
        self.flat = flat

        # Initialize variables
        self.src_history = []      # Close price history
        self.ma_history = []       # Moving average history
        self.slope_history = []    # Slope history
        self.up_history = []       # Uptrend history
        self.down_history = []     # Downtrend history
        self.swing_history = []    # Swing state history
        self.ma = None             # Current moving average value
        self.swing = 0             # Current swing state

        # Calculate alpha values
        self.minAlpha = 2 / (self.minLength + 1)
        self.majAlpha = 2 / (self.majLength + 1)

    def update(self, src):
        """
        Update the indicator with the latest closing price.
        """
        self.src_history.append(src)

        # Calculate highest high and lowest low over 'length + 1' periods
        hh_period = self.length + 1
        if len(self.src_history) >= hh_period:
            hh = max(self.src_history[-hh_period:], key=lambda k: k.high).high
            ll = min(self.src_history[-hh_period:], key=lambda k: k.low).low
        else:
            # Not enough data; use available data
            hh = max(self.src_history, key=lambda k: k.high).high
            ll = min(self.src_history, key=lambda k: k.low).low

        # Calculate 'mult' factor
        if hh - ll != 0:
            mult = abs(2 * src.close - ll - hh) / (hh - ll)
        else:
            mult = 0

        # Calculate 'final' alpha
        final = mult * (self.minAlpha - self.majAlpha) + self.majAlpha

        # Update the moving average (ma)
        if self.ma is None:
            # Initialize ma with the first price
            self.ma = src.close
        else:
            self.ma = self.ma + (final ** 2) * (src.close - self.ma)
        self.ma_history.append(self.ma)

        # Calculate the slope
        slope = self.calculate_slope()
        self.slope_history.append(slope)

        # Determine trend direction
        up = slope >= self.flat
        down = slope <= -self.flat
        self.up_history.append(up)
        self.down_history.append(down)

        # Generate buy and sell signals
        buy = False
        sell = False
        if len(self.up_history) >= 2:
            prev_up = self.up_history[-2]
            prev_down = self.down_history[-2]
            buy = up and not prev_up
            sell = down and not prev_down

        # Update swing state
        prev_swing = self.swing
        if buy and self.swing <= 0:
            self.swing = 1
        elif sell and self.swing >= 0:
            self.swing = -1

        self.swing_history.append(self.swing)

        # Determine long and short signals
        longsignal = self.swing == 1 and prev_swing != 1
        shortsignal = self.swing == -1 and prev_swing != -1

        # Return the current indicator values and signals
        return {
            'ma': self.ma,
            'slope': slope,
            'longsignal': longsignal,
            'shortsignal': shortsignal
        }

    def calculate_slope(self):
        """
        Calculate the slope of the moving average.
        """
        if len(self.ma_history) >= 3:
            ma = self.ma_history[-1]
            ma_2 = self.ma_history[-3]  # Value from two periods ago
            src = self.src_history[-1]
        else:
            # Not enough data to calculate slope
            return 0

        # Calculate highest high and lowest low over 'slopePeriod' periods
        if len(self.src_history) >= self.slopePeriod:
            highestHigh = max(self.src_history[-self.slopePeriod:], key=lambda k: k.high).high
            lowestLow = min(self.src_history[-self.slopePeriod:], key=lambda k: k.low).low
        else:
            highestHigh = max(self.src_history, key=lambda k: k.high).high
            lowestLow = min(self.src_history, key=lambda k: k.low).low

        # Prevent division by zero
        if highestHigh - lowestLow != 0:
            slope_range = self.slopeInRange / (highestHigh - lowestLow) * lowestLow
        else:
            slope_range = 0

        # Calculate 'dt' for the slope angle
        dt = (ma_2 - ma) / src.close * slope_range if src != 0 else 0
        c = math.sqrt(1 + dt * dt)

        # Ensure the value inside 'acos' is within [-1, 1]
        acos_input = 1 / c if c != 0 else 0
        acos_input = max(min(acos_input, 1), -1)

        xAngle = round(180 * math.acos(acos_input) / math.pi)
        maAngle = -xAngle if dt > 0 else xAngle

        return maAngle

    def ready(self):
        """
        Check if the indicator is ready.
        """
        return len(self.src_history) >= self.length + 1
