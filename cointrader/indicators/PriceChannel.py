from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline


class PriceChannel(Indicator):
    def __init__(self, name='price_channel', period=20):
        """
        Price Channel Indicator
        :param name: Name of the indicator
        :param period: Lookback period for calculating high and low
        """
        super().__init__(name)
        self.period = period
        self.reset()

    def reset(self):
        """
        Resets the indicator state
        """
        self.highs = deque(maxlen=self.period)
        self.lows = deque(maxlen=self.period)
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        """
        Update the indicator with a new Kline
        :param kline: Kline object containing OHLC data
        :return: A dictionary with the highest high, lowest low, and middle value
        """
        self.highs.append(kline.high)
        self.lows.append(kline.low)

        # Check if the indicator is ready
        if len(self.highs) == self.period and len(self.lows) == self.period:               
            high = max(self.highs)
            low = min(self.lows)
            middle = (high + low) / 2

            self._last_value = {'high': high, 'low': low, 'middle': middle}
        else:
            self._last_value = None

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        """
        Get the last calculated Price Channel values
        :return: A dictionary with the highest high, lowest low, and middle value
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline object used to update the indicator
        :return: Kline object
        """
        return self._last_kline

    def ready(self) -> bool:
        """
        Check if the indicator is ready to provide values
        :return: True if the indicator has enough data, False otherwise
        """
        return  len(self.highs) == self.period and len(self.lows) == self.period

    def increasing(self) -> bool:
        """
        Check if the middle value is increasing
        :return: True if the middle value is increasing, False otherwise
        """
        if len(self.highs) < 2 or self._last_value is None:
            return False
        current_middle = self._last_value['middle']
        previous_middle = (max(list(self.highs)[:-1]) + min(list(self.lows)[:-1])) / 2
        return current_middle > previous_middle

    def decreasing(self) -> bool:
        """
        Check if the middle value is decreasing
        :return: True if the middle value is decreasing, False otherwise
        """
        if len(self.highs) < 2 or self._last_value is None:
            return False
        current_middle = self._last_value['middle']
        previous_middle = (max(list(self.highs)[:-1]) + min(list(self.lows)[:-1])) / 2
        return current_middle < previous_middle
