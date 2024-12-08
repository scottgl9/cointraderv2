# Volume weighted average price
# The theory is that if the price of a buy trade is lower than the VWAP, it is a good trade. The opposite is true if the price is higher than the VWAP.
# The VWAP is calculated by (SUM(number_shares_bought) * SharePrice) / total_shares_bought

# 1. Calculate the Typical Price for the period. [(High + Low + Close)/3)]
# 2. Multiply the Typical Price by the period Volume (Typical Price x Volume)
# 3. Create a Cumulative Total of Typical Price. Cumulative(Typical Price x Volume)
# 4. Create a Cumulative Total of Volume. Cumulative(Volume)
# 5. Divide the Cumulative Totals.
# VWAP = Cumulative(Typical Price x Volume) / Cumulative(Volume)
from cointrader.common.Kline import Kline
from cointrader.common.Indicator import Indicator

class VWAP(Indicator):
    def __init__(self, name='vwap', period=14):
        super().__init__(name)
        self.period = period
        self.reset()

    def reset(self):
        self.volumes = []
        self.pricevolumes = []
        self.age = 0
        self.typical_price_sum = 0.0
        self.pricevolume_sum = 0.0
        self.volume_sum = 0.0
        self._last_kline = None
        self._last_value = None

    def ready(self):
        return len(self.volumes) == self.period

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close, kline.low, kline.high, kline.volume)
        self._last_kline = kline
        return result

    def update_with_value(self, close, low=0, high=0, volume=0):
        pricevolume = ((high + low + close) / 3.0) * volume
        if len(self.pricevolumes) < self.period:
            tail_pricevolume = 0.0
            self.pricevolumes.append(float(pricevolume))
        else:
            tail_pricevolume = self.pricevolumes[self.age]
            self.pricevolumes[int(self.age)] = float(pricevolume)

        if len(self.volumes) < self.period:
            tail_volume = 0.0
            self.volumes.append(float(volume))
        else:
            tail_volume = self.volumes[self.age]
            self.volumes[int(self.age)] = float(volume)

        self.pricevolume_sum += float(pricevolume) - tail_pricevolume
        self.volume_sum += float(volume) - tail_volume
        self.age = (self.age + 1) % self.period

        if len(self.volumes) != 0 and len(self.pricevolumes) != 0:
            self._last_value = self.pricevolume_sum / self.volume_sum

        return self._last_value
    
    def get_last_value(self):
        return self._last_value
    
    def get_last_kline(self):
        return self._last_kline
