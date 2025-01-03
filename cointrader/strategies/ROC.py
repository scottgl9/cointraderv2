from cointrader.common.Strategy import Strategy
from cointrader.signals.ROCSignal import ROCSignal

class ROC(Strategy):
    def __init__(self, symbol: str, name='roc', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.roc = ROCSignal(symbol=self._symbol, period=14)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.roc.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.roc.ready() and self.roc.cross_up():
            self._buy_signal_name = self.roc.name()
            return True
        return False

    def sell_signal(self):
        if self.roc.ready() and self.roc.cross_down():
            self._sell_signal_name = self.roc.name()
            return True
        return False

