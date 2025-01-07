from cointrader.common.Strategy import Strategy
from cointrader.signals.CMFSignal import CMFSignal

class CMF(Strategy):
    def __init__(self, symbol: str, name='cmf_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.cmf = CMFSignal(symbol=self._symbol, period=20)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.cmf.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.cmf.ready() and self.cmf.cross_up():
            self._buy_signal_name = self.cmf.name()
            return True
        return False

    def sell_signal(self):
        if self.cmf.ready() and self.cmf.cross_down():
            self._sell_signal_name = self.cmf.name()
            return True
        return False
