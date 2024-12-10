from collections import deque
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.EMA import EMA

class TRIX(Indicator):
    def __init__(self, name='trix', ema_period=15, signal_period=9):
        """
        Initialize the TRIX indicator.

        Parameters:
        - name (str): Name of the indicator.
        - ema_period (int): Period for the EMA calculations.
        - signal_period (int): Period for the signal line SMA.
        """
        super().__init__(name)
        self.ema_period = ema_period
        self.signal_period = signal_period
        self.reset()

    def reset(self):
        """
        Reset the TRIX indicator to its initial state.
        """
        # Initialize three EMA instances
        self.ema1 = EMA(name='ema1', period=self.ema_period)
        self.ema2 = EMA(name='ema2', period=self.ema_period)
        self.ema3 = EMA(name='ema3', period=self.ema_period)
        
        # Initialize a deque to store TRIX values for the signal line
        self.trix_values = deque(maxlen=self.signal_period)
        
        # Initialize the signal line value
        self.signal_line = None
        
        # Initialize previous EMA3 value for TRIX calculation
        self.prev_ema3 = None
        
        # Reset last value and last kline
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        """
        Update the TRIX indicator with a new Kline.

        Parameters:
        - kline (Kline): The new kline data.

        Returns:
        - trix (float or None): The updated TRIX value, or None if not enough data.
        """
        # Update the first EMA with the closing price
        current_ema1 = self.ema1.update(kline)
        
        # Update the second EMA with ema1's last value
        current_ema2 = self.ema2.update_with_value(current_ema1)
        
        # Update the third EMA with ema2's last value
        current_ema3 = self.ema3.update_with_value(current_ema2)
        
        # Check if all EMAs are ready
        if self.ema3.ready():
            if self.prev_ema3 is not None:
                # Calculate TRIX as percentage change of EMA3
                trix = ((current_ema3 - self.prev_ema3) / self.prev_ema3) * 100
                # Append to TRIX values deque
                self.trix_values.append(trix)
                
                # Calculate signal line if enough TRIX values
                if len(self.trix_values) == self.signal_period:
                    self.signal_line = sum(self.trix_values) / self.signal_period
                else:
                    self.signal_line = None
                
                # Update previous EMA3
                self.prev_ema3 = current_ema3
                
                # Update the last value
                self._last_value = trix
            else:
                # Initialize previous EMA3
                self.prev_ema3 = current_ema3
                # Not enough data to calculate TRIX
                self._last_value = None
        else:
            # EMAs are not ready yet
            self._last_value = None
        
        # Update the last kline
        self._last_kline = kline
        
        return self._last_value

    def increasing(self) -> bool:
        """
        Determine if the TRIX is increasing.

        Returns:
        - bool: True if TRIX is increasing, False otherwise.
        """
        if len(self.trix_values) < 2:
            return False
        return self.trix_values[-1] > self.trix_values[-2]

    def decreasing(self) -> bool:
        """
        Determine if the TRIX is decreasing.

        Returns:
        - bool: True if TRIX is decreasing, False otherwise.
        """
        if len(self.trix_values) < 2:
            return False
        return self.trix_values[-1] < self.trix_values[-2]

    def get_last_value(self):
        """
        Get the last TRIX value.

        Returns:
        - float or None: The last TRIX value, or None if not available.
        """
        return self._last_value

    def get_last_kline(self):
        """
        Get the last Kline.

        Returns:
        - Kline or None: The last Kline, or None if not available.
        """
        return self._last_kline

    def ready(self):
        """
        Check if the TRIX indicator is ready (has enough data).

        Returns:
        - bool: True if TRIX and signal line are ready, False otherwise.
        """
        # TRIX is ready if all three EMAs are ready and TRIX has at least signal_period values
        return self.ema3.ready() and len(self.trix_values) == self.signal_period

    def get_signal_line(self):
        """
        Get the current signal line value.

        Returns:
        - float or None: The signal line value, or None if not available.
        """
        return self.signal_line
