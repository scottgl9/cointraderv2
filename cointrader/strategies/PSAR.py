from cointrader.common.Strategy import Strategy
from cointrader.signals.PSARSignal import PSARSignal

class PSAR(Strategy):
    def __init__(self, symbol: str, name='psar_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.psar = PSARSignal(symbol=self._symbol, step=0.02, max_step=0.2)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.psar.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.psar.ready() and self.psar.cross_up():
            self._buy_signal_name = self.psar.name()
            return True
        return False

    def sell_signal(self):
        if self.psar.ready() and self.psar.cross_down():
            self._sell_signal_name = self.psar.name()
            return True
        return False
