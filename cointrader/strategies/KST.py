from cointrader.common.Strategy import Strategy
from cointrader.signals.KSTSignal import KSTSignal

class KST(Strategy):
    def __init__(self, symbol: str, name='kst', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self._kst = KSTSignal(symbol=self._symbol)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self._kst.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self._kst.ready() and self._kst.above() and self._kst.cross_up():
            self._buy_signal_name = self._kst.name()
            return True
        return False

    def sell_signal(self):
        if self._kst.ready() and self._kst.below() and self._kst.cross_down():
            self._sell_signal_name = self._kst.name()
            return True
        return False

