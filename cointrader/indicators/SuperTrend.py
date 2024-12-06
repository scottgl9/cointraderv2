from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from cointrader.indicators.ATR import ATR
from cointrader.indicators.EMA import EMA

# https://eodhd.com/financial-academy/backtesting-strategies-examples/a-step-by-step-guide-to-implementing-the-supertrend-indicator-in-python

class SuperTrend(Indicator):
    def __init__(self, name='supertrend', period=14, multiplier=3.0):
        Indicator.__init__(self, name)
        self.period = period
        self.multiplier = multiplier
        self.atr = ATR(period=period)
        self.emas = EMA(period=period)
        self.reset()

    def update(self, kline: Kline):
        result = self.atr.update(kline)
        #result = self.emas.update_with_value(result)
        if not self.atr.ready():
            self._last_kline = kline 
            return self._last_value
        atr = self.atr.get_last_value()
        hl2 = (kline.high + kline.low) / 2
        self._basic_upper = hl2 + atr * self.multiplier
        self._basic_lower = hl2 - atr * self.multiplier

        if self._last_kline is None:
            #self._prev_final_upper = 0.0
            #self._prev_final_lower = 0.0
            #self._prev_super_trend = 0.0
            #self._cur_super_trend = 0.0
            self._last_kline = kline
            return self._last_value

        # calculate final upper band
        if self._prev_final_upper is None:
            self._prev_final_upper = self._basic_upper
            self._cur_final_upper = self._basic_upper
        elif self._basic_upper < self._prev_final_upper or self._last_kline.close > self._prev_final_upper:
            # IF C.BUB < P.FUB OR P.CLOSE > P.FUB: C.FUB = C.BUB
            self._cur_final_upper = self._basic_upper
        #else:
        #    # ELSE: C.FUB = P.FUB
        #    self._cur_final_upper = self._prev_final_upper

        # calculate final lower band
        if self._prev_final_lower is None:
            self._prev_final_lower = self._basic_lower
            self._cur_final_lower = self._basic_lower
        elif self._basic_lower > self._prev_final_lower or self._last_kline.close < self._prev_final_lower:
            # IF C.BLB > P.FLB OR P.CLOSE < P.FLB: C.FLB = C.BLB
            self._cur_final_lower = self._basic_lower
        #else:
        #    #    # ELSE: C.FLB = P.FLB
        #    self._cur_final_lower = self._prev_final_lower

        #IF P.ST == P.FUB AND C.CLOSE < C.FUB: C.ST = C.FUB
        #IF P.ST == P.FUB AND C.CLOSE > C.FUB: C.ST = C.FLB
        #IF P.ST == P.FLB AND C.CLOSE > C.FLB: C.ST = C.FLB
        #IF P.ST == P.FLB AND C.CLOSE < C.FLB: C.ST = C.FUB
        if self._prev_super_trend is None:
            if kline.close < self._cur_final_upper:
                self._cur_super_trend = self._cur_final_upper
            else:
                self._cur_super_trend = self._cur_final_lower
        elif self._prev_super_trend == self._prev_final_upper and kline.close <= self._cur_final_upper:
            self._cur_super_trend = self._cur_final_upper
        elif self._prev_super_trend == self._prev_final_upper and kline.close > self._cur_final_upper:
            self._cur_super_trend = self._cur_final_lower
        elif self._prev_super_trend == self._prev_final_lower and kline.close >= self._cur_final_lower:
            self._cur_super_trend = self._cur_final_lower
        elif self._prev_super_trend == self._prev_final_lower and kline.close < self._cur_final_lower:
            self._cur_super_trend = self._cur_final_upper

        self._last_value = self._cur_super_trend
        self._prev_super_trend = self._cur_super_trend
        self._prev_final_lower = self._cur_final_lower
        self._prev_final_upper = self._cur_final_upper
        self._last_kline = kline

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def reset(self):
        self._last_kline = None
        self._last_value = None
        self._basic_upper = 0.0
        self._basic_lower = 0.0
        self._cur_final_upper = None
        self._cur_final_lower = None
        self._cur_super_trend = None
        self._prev_final_upper = None
        self._prev_final_lower = None
        self._prev_super_trend = None
        self.atr.reset()

    def ready(self):
        return self.atr.ready() and self._last_value is not None
