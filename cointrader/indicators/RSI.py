from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class RSI(Indicator):
    def __init__(self, name='rsi', period=14, smoother=None, unit_scale=False):
        Indicator.__init__(self, name)
        self.period = period
        # unit scale sets rsi values in range [0, 1] instead of [0, 100]
        self.unit_scale = unit_scale
        self._sum_up = 0
        self._sum_down = 0
        self._prev_avg_up = 0
        self._prev_avg_down = 0
        self._avg_up = 0
        self._avg_down = 0
        self._last_u = 0
        self._last_d = 0
        self.up_values = []
        self.down_values = []
        self.age = 0
        self.last_close = 0
        self.rs = 0
        self.result = 0
        self.smoother = smoother

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result

    def update_with_value(self, value):
        close = value

        if self.last_close == 0:
            self.last_close = float(close)
            self.up_values.append(0.0)
            self.down_values.append(0.0)
            return self.result

        if len(self.up_values) < self.period:
            if float(close) > self.last_close:
                u = float(close) - self.last_close
                d = 0.0
                self._sum_up += u
            else:
                u = 0.0
                d = self.last_close - float(close)
                self._sum_down += d
            self.up_values.append(u)
            self.down_values.append(d)
        else:
            if float(close) > self.last_close:
                u = float(close) - self.last_close
                d = 0
                self._sum_up += u
            elif float(close) < self.last_close:
                u = 0
                d = self.last_close - float(close)
                self._sum_down += d
            else:
                u = 0
                d = 0

            self._sum_up -= self.up_values[int(self.age)]
            self._sum_down -= self.down_values[int(self.age)]
            self.up_values[int(self.age)] = u
            self.down_values[int(self.age)] = d
            self.age = (self.age + 1) % self.period

            self._prev_avg_up = self._avg_up
            self._prev_avg_down = self._avg_down
            self._avg_up = self._sum_up / self.period
            self._avg_down = self._sum_down / self.period

            if not self.rs:
                rs1 = self._avg_up
                rs2 = self._avg_down
                self.rs = rs1 / rs2
            else:
                rs1 = ((self.period - 1) * self._prev_avg_up + u)
                rs2 = ((self.period - 1) * self._prev_avg_down + d)
                if rs2:
                    self.rs = rs1 / rs2
            if not rs2:
                self.result = 100.0
            else:
                if self.unit_scale:
                    result = 1.0 - (1.0 / (1.0 + self.rs))
                else:
                    result = 100.0 - (100.0 / (1.0 + self.rs))
                if self.smoother:
                    self.result = self.smoother.update(result)
                else:
                    self.result = result

        self.last_close = float(close)

        self._last_value = self.result

        return self.result

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline

    def reset(self):
        self.up_values = []
        self.down_values = []
    
    def ready(self):
        return len(self.up_values) == self.period