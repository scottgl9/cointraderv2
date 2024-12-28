# This file implements the Know Sure Thing (KST) indicator.
from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.ROC import ROC
from cointrader.indicators.SMA import SMA

class KST(Indicator):
    def __init__(self, name='kst', roc_periods=[10, 15, 20, 30], smoothing_periods=[10, 10, 10, 15], weights=[1, 2, 3, 4], signal_period=9):
        """
        Initialize the Know Sure Thing (KST) indicator.
        :param roc_periods: List of ROC periods for the four timeframes.
        :param smoothing_periods: List of smoothing periods for the four ROCs.
        :param weights: List of weights for the smoothed ROCs.
        :param signal_period: Period for the signal line.
        """
        super().__init__(name)
        self.roc_periods = roc_periods
        self.smoothing_periods = smoothing_periods
        self.weights = weights
        self.signal_period = signal_period

        # Initialize the ROC and SMA indicators for each timeframe
        self.rocs = [ROC(name=f'{name}_roc_{i}', period=roc_period) for i, roc_period in enumerate(roc_periods)]
        self.smas = [SMA(name=f'{name}_sma_{i}', period=smoothing_period) for i, smoothing_period in enumerate(smoothing_periods)]
        self.signal_sma = SMA(name=f'{name}_signal', period=signal_period)

        self.reset()

    def reset(self):
        """
        Reset the KST indicator.
        """
        for roc in self.rocs:
            roc.reset()
        for sma in self.smas:
            sma.reset()
        self.signal_sma.reset()
        self._last_value = None

    def update(self, kline: Kline):
        """
        Update the KST indicator with a new Kline.
        :param kline: The current Kline.
        """
        smoothed_rocs = []
        for roc, sma in zip(self.rocs, self.smas):
            # Update the ROC with the current Kline
            roc_value = roc.update(kline)

            # Update the SMA with the ROC value (if available)
            if roc_value is not None:
                smoothed_roc = sma.update_with_value(roc_value)
                if smoothed_roc is not None:
                    smoothed_rocs.append(smoothed_roc)

        # Ensure we have enough data for all smoothed ROCs
        if len(smoothed_rocs) < len(self.weights):
            return self._last_value

        # Calculate the weighted sum of smoothed ROCs to get the KST value
        kst_value = sum(weight * smoothed_roc for weight, smoothed_roc in zip(self.weights, smoothed_rocs))

        # Update the signal line SMA with the KST value
        signal_value = self.signal_sma.update_with_value(kst_value)

        # Update internal state
        self._last_value = {"kst": kst_value, "signal": signal_value}
        return self._last_value

    def get_last_value(self):
        """
        Get the last calculated KST and Signal Line values as a dictionary.
        """
        return self._last_value

    def ready(self):
        """
        Check if the KST indicator is ready for use.
        """
        return (
            all(roc.ready() for roc in self.rocs)
            and all(sma.ready() for sma in self.smas)
            and self.signal_sma.ready() and self._last_value is not None
        )
