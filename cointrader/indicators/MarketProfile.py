# THis file contains the implementation of the Market Profile indicator.
from collections import deque, defaultdict
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
import math

class MarketProfile(Indicator):
    def __init__(self, name='market_profile', period=100, value_area_percentage=70):
        """
        Initialize the Market Profile indicator.

        :param name: Name of the indicator.
        :param period: Number of recent Klines to include in the Market Profile.
        :param value_area_percentage: Percentage of total TPOs to include within the Value Area.
        """
        super().__init__(name)
        self.period = period
        self.value_area_percentage = value_area_percentage

        # Rolling window of Klines
        self.klines = deque(maxlen=self.period)

        # Profile dictionary to store TPO counts
        self.profile = defaultdict(int)

        # Key metrics
        self.poc = None
        self.vah = None
        self.val = None

        # Initial Balance (optional)
        self.initial_balance_high = None
        self.initial_balance_low = None
        self.ib_period = 20  # Define IB period (e.g., first 20 Klines)

        self._last_kline = None
        self._last_value = None

    def reset(self):
        """
        Reset the Market Profile indicator to its initial state.
        """
        self.klines.clear()
        self.profile.clear()
        self.poc = None
        self.vah = None
        self.val = None
        self.initial_balance_high = None
        self.initial_balance_low = None
        self._last_kline = None
        self._last_value = None

    def _initialize_profile(self):
        """
        Initialize the profile dictionary based on the current rolling window.
        """
        self.profile.clear()
        for kline in self.klines:
            self._add_tpos(kline)
        self._calculate_key_metrics()

    def _add_tpos(self, kline: Kline):
        """
        Add TPOs for a given Kline to the profile.

        :param kline: The Kline to add TPOs from.
        """
        # Determine price levels covered by the Kline
        # Assuming price levels are whole numbers; adjust binning as needed
        start_price = math.floor(kline.low)
        end_price = math.ceil(kline.high)
        for price in range(start_price, end_price + 1):
            self.profile[price] += 1

    def _remove_tpos(self, kline: Kline):
        """
        Remove TPOs for a given Kline from the profile.

        :param kline: The Kline to remove TPOs from.
        """
        # Determine price levels covered by the Kline
        start_price = math.floor(kline.low)
        end_price = math.ceil(kline.high)
        for price in range(start_price, end_price + 1):
            if self.profile[price] > 0:
                self.profile[price] -= 1
                if self.profile[price] == 0:
                    del self.profile[price]

    def _calculate_key_metrics(self):
        """
        Calculate POC, VAH, and VAL based on the current profile.
        """
        if not self.profile:
            self.poc = None
            self.vah = None
            self.val = None
            return

        # Point of Control (POC)
        self.poc = max(self.profile, key=self.profile.get)

        # Value Area (VA)
        total_tpos = sum(self.profile.values())
        target_tpos = (self.value_area_percentage / 100.0) * total_tpos

        # Sort price levels by TPO count descending
        sorted_profile = sorted(self.profile.items(), key=lambda x: x[1], reverse=True)

        cumulative_tpos = 0
        value_area_prices = []
        for price, count in sorted_profile:
            cumulative_tpos += count
            value_area_prices.append(price)
            if cumulative_tpos >= target_tpos:
                break

        if value_area_prices:
            self.vah = max(value_area_prices)
            self.val = min(value_area_prices)
        else:
            self.vah = None
            self.val = None

    def update(self, kline: Kline):
        """
        Update the Market Profile with a new Kline.

        :param kline: The new Kline data.
        :return: A dictionary with 'poc', 'vah', 'val', and 'profile' or None if not ready.
        """
        if len(self.klines) == self.period:
            # Remove the oldest Kline and adjust the profile
            old_kline = self.klines.popleft()
            self._remove_tpos(old_kline)

        # Append the new Kline
        self.klines.append(kline)

        # Add TPOs for the new Kline
        self._add_tpos(kline)

        # Initialize Initial Balance (IB) if within the first IB period
        if len(self.klines) == self.ib_period and self.initial_balance_high is None and self.initial_balance_low is None:
            self.initial_balance_high = max(kline.high for kline in list(self.klines))
            self.initial_balance_low = min(kline.low for kline in list(self.klines))
            print(f"Initial Balance set: High={self.initial_balance_high}, Low={self.initial_balance_low}")

        # Calculate key metrics
        self._calculate_key_metrics()

        # Store the latest metrics
        if self.ready():
            self._last_value = {
                'poc': self.poc,
                'vah': self.vah,
                'val': self.val,
                'profile': dict(self.profile)
            }
        else:
            self._last_value = None

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        """
        Get the latest Market Profile metrics.

        :return: A dictionary with 'poc', 'vah', 'val', and 'profile' or None.
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline used to compute the Market Profile.

        :return: The last Kline object or None.
        """
        return self._last_kline

    def ready(self):
        """
        Check if the Market Profile is ready to provide metrics.

        :return: True if ready, False otherwise.
        """
        return len(self.klines) == self.period and self.poc is not None and self.vah is not None and self.val is not None
