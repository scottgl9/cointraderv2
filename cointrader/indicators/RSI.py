from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class RSI(Indicator):
    def __init__(self, name='rsi', period=14):
        Indicator.__init__(self, name)
        self.period = period
        self.reset()

    def reset(self):
        self._up_values = []
        self._down_values = []
        self._sum_up = 0
        self._sum_down = 0
        self._prev_avg_up = 0
        self._prev_avg_down = 0
        self._avg_up = 0
        self._avg_down = 0
        self._last_u = 0
        self._last_d = 0
        self._age = 0
        self._last_close = 0
        self._rs = 0
        self._last_value = None
        self._last_kline = None

    def update(self, kline: Kline):
        result = self.update_with_value(kline.close)
        self._last_kline = kline
        return result

    def update_with_value(self, value):
        close = value

        if self._last_close == 0:
            self._last_close = float(close)
            self._up_values.append(0.0)
            self._down_values.append(0.0)
            return self._last_value

        if len(self._up_values) < self.period:
            if float(close) > self._last_close:
                u = float(close) - self._last_close
                d = 0.0
                self._sum_up += u
            else:
                u = 0.0
                d = self._last_close - float(close)
                self._sum_down += d
            self._up_values.append(u)
            self._down_values.append(d)
        else:
            if float(close) > self._last_close:
                u = float(close) - self._last_close
                d = 0
                self._sum_up += u
            elif float(close) < self._last_close:
                u = 0
                d = self._last_close - float(close)
                self._sum_down += d
            else:
                u = 0
                d = 0

            self._sum_up -= self._up_values[int(self._age)]
            self._sum_down -= self._down_values[int(self._age)]
            self._up_values[int(self._age)] = u
            self._down_values[int(self._age)] = d
            self._age = (self._age + 1) % self.period

            self._prev_avg_up = self._avg_up
            self._prev_avg_down = self._avg_down
            self._avg_up = self._sum_up / self.period
            self._avg_down = self._sum_down / self.period

            if not self._rs:
                rs1 = self._avg_up
                rs2 = self._avg_down
                if rs2 != 0:
                    self._rs = rs1 / rs2
                else:
                    self._rs = 0
            else:
                rs1 = ((self.period - 1) * self._prev_avg_up + u)
                rs2 = ((self.period - 1) * self._prev_avg_down + d)
                if rs2 != 0:
                    self._rs = rs1 / rs2
                else:
                    self._rs = 0
            if not rs2:
                self._last_value = 100.0
            else:
                self._last_value = 100.0 - (100.0 / (1.0 + self._rs))

        self._last_close = float(close)

        return self._last_value

    def get_last_value(self):
        return self._last_value

    def get_last_kline(self):
        return self._last_kline
   
    def ready(self):
        return len(self._up_values) == self.period and self._last_value is not None