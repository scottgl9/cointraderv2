from cointrader.common.Strategy import Strategy
from cointrader.signals.SupertrendSignal import SupertrendSignal

class Supertrend(Strategy):
    def __init__(self, symbol: str, name='supertrend', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.supertrend = SupertrendSignal(symbol=self._symbol, period=14, multiplier=3)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.supertrend.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        return result

    def buy_signal(self):
        if not self.supertrend.ready():
            return False
        if self.supertrend.cross_up():
            self._buy_signal_name = self.supertrend.name()
            return True
        return False

    def sell_signal(self):
        if not self.supertrend.ready():
            return False
        if self.supertrend.cross_down():
            self._sell_signal_name = self.supertrend.name()
            return True
        return False
