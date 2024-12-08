from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.ROC import ROC
from cointrader.indicators.WMA import WMA

class CoppockCurve(Indicator):
    def __init__(self, name='coppock_curve', long_roc_period=14, short_roc_period=11, wma_period=10):
        super().__init__(name)
        self.long_roc_period = long_roc_period
        self.short_roc_period = short_roc_period
        self.wma_period = wma_period

        # Instantiate the two ROC indicators
        self.long_roc = ROC(period=self.long_roc_period)
        self.short_roc = ROC(period=self.short_roc_period)

        # Instantiate WMA indicator
        self.wma = WMA(period=self.wma_period)

        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        # Update the underlying ROC indicators with the current kline
        long_roc_val = self.long_roc.update(kline)
        short_roc_val = self.short_roc.update(kline)

        # Only compute sum if both ROCs are ready
        if long_roc_val is not None and short_roc_val is not None:
            roc_sum = long_roc_val + short_roc_val

            # Update WMA with the roc_sum value
            wma_val = self.wma.update_with_value(roc_sum)

            # If WMA is ready, we have our Coppock Curve value
            if wma_val is not None:
                self._last_value = wma_val
            else:
                self._last_value = None
        else:
            self._last_value = None

        self._last_kline = kline
        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def ready(self):
        # Coppock Curve is ready when WMA is ready and thus producing values
        return self._last_value is not None
