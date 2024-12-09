from collections import deque
import math
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class VolumeProfile(Indicator):
    def __init__(self, name='volume_profile', period=100, bins=50, value_area_percentage=70):
        """
        Initialize the Volume Profile indicator.

        :param name: Name of the indicator.
        :param period: Number of recent Klines to include in the Volume Profile.
        :param bins: Number of price bins to divide the price range into.
        :param value_area_percentage: Percentage of total volume to include in the Value Area.
        """
        super().__init__(name)
        self.period = period
        self.bins = bins
        self.value_area_percentage = value_area_percentage

        # Rolling window of Klines
        self.klines = deque(maxlen=self.period)

        # Volume distribution across price bins
        self.volume_distribution = [0 for _ in range(self.bins)]

        # Price range boundaries
        self.min_price = None
        self.max_price = None
        self.bin_size = None

        # Key metrics
        self.poc = None
        self.vah = None
        self.val = None

        self._last_kline = None
        self._last_value = None

    def reset(self):
        """
        Reset the Volume Profile indicator to its initial state.
        """
        self.klines.clear()
        self.volume_distribution = [0 for _ in range(self.bins)]
        self.min_price = None
        self.max_price = None
        self.bin_size = None
        self.poc = None
        self.vah = None
        self.val = None
        self._last_kline = None
        self._last_value = None

    def _initialize_bins(self):
        """
        Initialize the price bins based on the current rolling window of Klines.
        """
        if not self.klines:
            return

        highs = [kline.high for kline in self.klines]
        lows = [kline.low for kline in self.klines]
        self.max_price = max(highs)
        self.min_price = min(lows)
        self.bin_size = (self.max_price - self.min_price) / self.bins if self.bins > 0 else 1

        # Reset volume distribution
        self.volume_distribution = [0 for _ in range(self.bins)]

        # Populate initial volume distribution
        for kline in self.klines:
            self._distribute_volume(kline)

    def _distribute_volume(self, kline: Kline):
        """
        Distribute the volume of a single Kline across the price bins.

        :param kline: The Kline to distribute volume for.
        """
        if self.bin_size == 0:
            return  # Avoid division by zero

        high = kline.high
        low = kline.low
        volume = kline.volume

        # Determine which bins the Kline spans
        start_bin = int((low - self.min_price) / self.bin_size)
        end_bin = int((high - self.min_price) / self.bin_size)

        # Clamp bin indices to valid range
        start_bin = max(0, min(self.bins - 1, start_bin))
        end_bin = max(0, min(self.bins - 1, end_bin))

        if start_bin == end_bin:
            # Entire volume falls into a single bin
            self.volume_distribution[start_bin] += volume
        else:
            # Distribute volume across multiple bins proportionally
            for bin_idx in range(start_bin, end_bin + 1):
                bin_low = self.min_price + bin_idx * self.bin_size
                bin_high = bin_low + self.bin_size

                # Calculate overlap between Kline and bin
                overlap = max(0, min(high, bin_high) - max(low, bin_low))
                bin_range = bin_high - bin_low
                if bin_range > 0:
                    proportion = overlap / bin_range
                    self.volume_distribution[bin_idx] += volume * proportion

    def _remove_volume(self, kline: Kline):
        """
        Remove the volume of an old Kline from the volume distribution.

        :param kline: The Kline to remove volume for.
        """
        if self.bin_size == 0:
            return  # Avoid division by zero

        high = kline.high
        low = kline.low
        volume = kline.volume

        # Determine which bins the Kline spans
        start_bin = int((low - self.min_price) / self.bin_size)
        end_bin = int((high - self.min_price) / self.bin_size)

        # Clamp bin indices to valid range
        start_bin = max(0, min(self.bins - 1, start_bin))
        end_bin = max(0, min(self.bins - 1, end_bin))

        if start_bin == end_bin:
            # Entire volume falls into a single bin
            self.volume_distribution[start_bin] -= volume
        else:
            # Remove volume proportionally across multiple bins
            for bin_idx in range(start_bin, end_bin + 1):
                bin_low = self.min_price + bin_idx * self.bin_size
                bin_high = bin_low + self.bin_size

                # Calculate overlap between Kline and bin
                overlap = max(0, min(high, bin_high) - max(low, bin_low))
                bin_range = bin_high - bin_low
                if bin_range > 0:
                    proportion = overlap / bin_range
                    self.volume_distribution[bin_idx] -= volume * proportion

    def update(self, kline: Kline):
        """
        Update the Volume Profile with a new Kline.

        :param kline: The new Kline data.
        :return: A dictionary with 'poc', 'vah', 'val', and 'volume_distribution' or None if not ready.
        """
        if len(self.klines) == self.period:
            # Remove the oldest Kline and adjust volume distribution
            old_kline = self.klines.popleft()
            self._remove_volume(old_kline)

        # Append the new Kline
        self.klines.append(kline)

        if len(self.klines) == self.period and self.min_price is None and self.max_price is None:
            # Initialize bins on reaching the first full period
            self._initialize_bins()
        elif len(self.klines) == self.period:
            # Update bins dynamically
            # Check if price range has changed significantly
            highs = [kline.high for kline in self.klines]
            lows = [kline.low for kline in self.klines]
            new_max = max(highs)
            new_min = min(lows)

            if new_max > self.max_price or new_min < self.min_price:
                # Reinitialize bins to accommodate new price range
                self._initialize_bins()
            else:
                # Distribute volume for the new Kline
                self._distribute_volume(kline)

        # Calculate key metrics if ready
        if self.ready():
            total_volume = sum(self.volume_distribution)
            if total_volume == 0:
                # Avoid division by zero
                self.poc = None
                self.vah = None
                self.val = None
            else:
                # Point of Control (POC)
                max_volume = max(self.volume_distribution)
                poc_bin = self.volume_distribution.index(max_volume)
                self.poc = self.min_price + poc_bin * self.bin_size + self.bin_size / 2

                # Value Area (VA)
                sorted_bins = sorted(
                    [(idx, vol) for idx, vol in enumerate(self.volume_distribution)],
                    key=lambda x: x[1],
                    reverse=True
                )
                cumulative_volume = 0
                target_volume = (self.value_area_percentage / 100.0) * total_volume
                va_bins = []
                for idx, vol in sorted_bins:
                    cumulative_volume += vol
                    va_bins.append(idx)
                    if cumulative_volume >= target_volume:
                        break
                if va_bins:
                    va_high_bin = max(va_bins)
                    va_low_bin = min(va_bins)
                    self.vah = self.min_price + va_high_bin * self.bin_size + self.bin_size / 2
                    self.val = self.min_price + va_low_bin * self.bin_size + self.bin_size / 2
                else:
                    self.vah = None
                    self.val = None

            # Store the latest metrics
            self._last_value = {
                'poc': self.poc,
                'vah': self.vah,
                'val': self.val,
                'volume_distribution': self.volume_distribution.copy()
            }
        else:
            self._last_value = None

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        """
        Get the latest Volume Profile metrics.

        :return: A dictionary with 'poc', 'vah', 'val', and 'volume_distribution' or None.
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline used to compute the Volume Profile.

        :return: The last Kline object or None.
        """
        return self._last_kline

    def ready(self):
        """
        Check if the Volume Profile is ready to provide metrics.

        :return: True if ready, False otherwise.
        """
        return len(self.klines) == self.period and self.poc is not None and self.vah is not None and self.val is not None
