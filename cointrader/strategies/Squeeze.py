from cointrader.common.Strategy import Strategy
from cointrader.signals.SqueezeMomentumSignal import SqueezeMomentumSignal

class Squeeze(Strategy):
    def __init__(self, symbol: str, name='supertrend', granularity=0):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self._squeeze = SqueezeMomentumSignal(name='squeeze', symbol=self._symbol, length=20, multBB=2.0, multKC=1.5)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self._squeeze.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        return result

    def buy_signal(self):
        if self._squeeze.ready() and self._squeeze.cross_up():
            self._buy_signal_name = self._squeeze.name()
            return True
        return False

    def sell_signal(self):
        if self._squeeze.ready() and self._squeeze.cross_down():
            self._sell_signal_name = self._squeeze.name()
            return True
        return False
