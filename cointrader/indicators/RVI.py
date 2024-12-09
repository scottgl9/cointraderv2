# This file contains the implementation of the Relative Vigor Index (RVI) indicator.
from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.SMA import SMA  # Ensure SMA is correctly imported

class RelativeVigorIndex(Indicator):
    def __init__(self, name='relative_vigor_index', period=10, signal_period=4):
        """
        Initialize the Relative Vigor Index (RVI) indicator.
        
        :param name: Name of the indicator.
        :param period: The number of periods for calculating AvgBP and AvgTR.
        :param signal_period: The number of periods for the signal line SMA.
        """
        super().__init__(name)
        self.period = period
        self.signal_period = signal_period

        # Initialize deques to store BP and TR values
        self.bp_values = deque(maxlen=period)
        self.tr_values = deque(maxlen=period)

        # Initialize SMA instances for AvgBP and AvgTR
        self.sma_bp = SMA(name=f'sma_bp_{period}', period=period)
        self.sma_tr = SMA(name=f'sma_tr_{period}', period=period)

        # Initialize SMA for Signal Line
        self.sma_signal = SMA(name=f'sma_signal_{signal_period}', period=signal_period)

        # Internal state
        self._last_value = None
        self._last_kline = None

    def reset(self):
        """
        Reset the RVI indicator to its initial state.
        """
        self.bp_values.clear()
        self.tr_values.clear()
        self.sma_bp.reset()
        self.sma_tr.reset()
        self.sma_signal.reset()
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        """
        Update the RVI indicator with a new Kline.
        
        :param kline: The new Kline data.
        :return: A dictionary with 'rvi', 'signal', and 'histogram' or None if not ready.
        """
        close = kline.close
        open_ = kline.open
        high = kline.high
        low = kline.low

        # Calculate Buying Pressure (BP) and True Range (TR)
        bp = close - open_
        tr = high - low

        # Append to deques
        self.bp_values.append(bp)
        self.tr_values.append(tr)

        # Update SMA for BP and TR
        sma_bp_val = self.sma_bp.update_with_value(bp)
        sma_tr_val = self.sma_tr.update_with_value(tr)

        # Ensure both SMAs are ready before computing RVI
        if not (self.sma_bp.ready() and self.sma_tr.ready()):
            self._last_kline = kline
            self._last_value = None
            return None

        # Calculate RVI
        if self.sma_tr.get_last_value() == 0:
            rvi = 0.0  # Avoid division by zero
        else:
            rvi = (self.sma_bp.get_last_value() / self.sma_tr.get_last_value()) * 100.0

        # Update Signal Line SMA
        sma_signal_val = self.sma_signal.update_with_value(rvi)

        # Ensure Signal Line SMA is ready
        if not self.sma_signal.ready():
            self._last_kline = kline
            self._last_value = None
            return None

        # Calculate Histogram
        histogram = rvi - self.sma_signal.get_last_value()

        # Store the latest RVI values
        self._last_value = {
            'rvi': rvi,
            'signal': self.sma_signal.get_last_value(),
            'histogram': histogram
        }
        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        """
        Get the latest RVI value.
        
        :return: A dictionary with 'rvi', 'signal', and 'histogram' or None.
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline used to compute RVI.
        
        :return: The last Kline object or None.
        """
        return self._last_kline

    def ready(self):
        """
        Check if the RVI indicator is ready to provide values.
        
        :return: True if ready, False otherwise.
        """
        return self._last_value is not None
