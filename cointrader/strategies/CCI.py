from cointrader.common.Strategy import Strategy
from cointrader.signals.CCISignal import CCISignal

class CCI(Strategy):
    def __init__(self, symbol: str, name='cci_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.cci = CCISignal(symbol=self._symbol, period=20)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.cci.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.cci.ready() and self.cci.cross_up():
            self._buy_signal_name = self.cci.name()
            return True
        return False

    def sell_signal(self):
        if self.cci.ready() and self.cci.cross_down():
            self._sell_signal_name = self.cci.name()
            return True
        return False
