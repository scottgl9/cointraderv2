from collections import deque
from typing import Optional, Dict
import matplotlib.pyplot as plt

from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class HeikinAshi(Indicator):
    def __init__(self, name='heikin_ashi', period: int = 100):
        """
        Initialize the Heikin Ashi indicator.

        :param name: Name of the indicator.
        :param period: Number of recent Klines to consider.
        """
        super().__init__(name)
        self.period = period
        self.klines = deque(maxlen=self.period)
        self.ha_open: Optional[float] = None
        self.ha_close: Optional[float] = None
        self.ha_high: Optional[float] = None
        self.ha_low: Optional[float] = None
        self.heikin_ashi_candles = deque(maxlen=self.period)
        self._last_kline = None
        self._last_value = None

    def reset(self):
        """
        Reset the Heikin Ashi indicator to its initial state.
        """
        self.klines.clear()
        self.heikin_ashi_candles.clear()
        self.ha_open = None
        self.ha_close = None
        self.ha_high = None
        self.ha_low = None
        self._last_kline = None
        self._last_value = None

    def _calculate_heikin_ashi(self, kline: Kline) -> Dict[str, float]:
        """
        Calculate Heikin Ashi values based on the current and previous Heikin Ashi.

        :param kline: The current Kline data.
        :return: Dictionary containing HA_Open, HA_High, HA_Low, HA_Close.
        """
        close = kline.close
        open_ = kline.open
        high = kline.high
        low = kline.low

        # Calculate Heikin Ashi Close
        ha_close = (open_ + high + low + close) / 4

        if self.ha_open is None:
            # For the first candle, HA_Open is the same as the standard Open
            ha_open = open_
        else:
            # HA_Open is the average of the previous HA_Open and HA_Close
            ha_open = (self.ha_open + self.ha_close) / 2

        # HA_High is the max of High, HA_Open, HA_Close
        ha_high = max(high, ha_open, ha_close)

        # HA_Low is the min of Low, HA_Open, HA_Close
        ha_low = min(low, ha_open, ha_close)

        # Update previous HA_Open and HA_Close for the next calculation
        self.ha_open = ha_open
        self.ha_close = ha_close
        self.ha_high = ha_high
        self.ha_low = ha_low

        return {
            'open': ha_open,
            'high': ha_high,
            'low': ha_low,
            'close': ha_close
        }

    def update(self, kline: Kline) -> Optional[Dict[str, float]]:
        """
        Update the Heikin Ashi indicator with a new Kline.

        :param kline: The new Kline data.
        :return: Dictionary with HA_Open, HA_High, HA_Low, HA_Close or None if not ready.
        """
        self.klines.append(kline)
        self._last_kline = kline

        ha_values = self._calculate_heikin_ashi(kline)
        self.heikin_ashi_candles.append(ha_values)

        if len(self.heikin_ashi_candles) == self.period:
            self._last_value = ha_values
            return ha_values
        else:
            self._last_value = None
            return None

    def get_last_value(self) -> Optional[Dict[str, float]]:
        """
        Get the latest Heikin Ashi values.

        :return: Dictionary with HA_Open, HA_High, HA_Low, HA_Close or None.
        """
        return self._last_value

    def ready(self) -> bool:
        """
        Check if the Heikin Ashi indicator is ready to provide values.

        :return: True if ready, False otherwise.
        """
        return len(self.heikin_ashi_candles) == self.period

    def plot_heikin_ashi(self):
        """
        Plot Heikin Ashi candlesticks alongside traditional candlesticks.

        Note: This function requires matplotlib and should be called after the indicator is ready.
        """
        if not self.ready():
            print("Heikin Ashi not ready to plot.")
            return

        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import pandas as pd

        # Prepare data for plotting
        dates = [k.time for k in self.klines]
        traditional_open = [k.open for k in self.klines]
        traditional_high = [k.high for k in self.klines]
        traditional_low = [k.low for k in self.klines]
        traditional_close = [k.close for k in self.klines]

        ha_open = [ha['HA_Open'] for ha in self.heikin_ashi_candles]
        ha_high = [ha['HA_High'] for ha in self.heikin_ashi_candles]
        ha_low = [ha['HA_Low'] for ha in self.heikin_ashi_candles]
        ha_close = [ha['HA_Close'] for ha in self.heikin_ashi_candles]

        fig, axes = plt.subplots(2, 1, figsize=(15, 10), sharex=True)

        # Traditional Candlesticks
        axes[0].set_title('Traditional Candlestick Chart')
        for i in range(len(dates)):
            color = 'green' if traditional_close[i] >= traditional_open[i] else 'red'
            axes[0].plot([dates[i], dates[i]], [traditional_low[i], traditional_high[i]], color='black')
            axes[0].fill_between([dates[i] - pd.Timedelta(minutes=1), dates[i] + pd.Timedelta(minutes=1)],
                                 traditional_open[i], traditional_close[i],
                                 color=color, alpha=0.7)

        # Heikin Ashi Candlesticks
        axes[1].set_title('Heikin Ashi Candlestick Chart')
        for i in range(len(dates)):
            color = 'green' if ha_close[i] >= ha_open[i] else 'red'
            axes[1].plot([dates[i], dates[i]], [ha_low[i], ha_high[i]], color='black')
            axes[1].fill_between([dates[i] - pd.Timedelta(minutes=1), dates[i] + pd.Timedelta(minutes=1)],
                                 ha_open[i], ha_close[i],
                                 color=color, alpha=0.7)

        axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
        plt.tight_layout()
        plt.show()
