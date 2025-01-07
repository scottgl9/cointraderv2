from cointrader.common.Strategy import Strategy
from cointrader.signals.EOMSignal import EOMSignal

class EOM(Strategy):
    def __init__(self, symbol: str, name='eom_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.eom = EOMSignal(symbol=self._symbol, period=14)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.eom.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.eom.ready() and self.eom.cross_up():
            self._buy_signal_name = self.eom.name()
            return True
        return False

    def sell_signal(self):
        if self.eom.ready() and self.eom.cross_down():
            self._sell_signal_name = self.eom.name()
            return True
        return False
