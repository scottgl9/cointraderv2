from cointrader.common.Strategy import Strategy
from cointrader.signals.RVISignal import RVISignal

class RVI(Strategy):
    def __init__(self, symbol: str, name='rvi_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.rvi = RVISignal(symbol=self._symbol)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.rvi.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.rvi.ready() and self.rvi.cross_up():
            self._buy_signal_name = self.rvi.name()
            return True
        return False

    def sell_signal(self):
        if self.rvi.ready() and self.rvi.cross_down():
            self._sell_signal_name = self.rvi.name()
            return True
        return False
