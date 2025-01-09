from cointrader.common.Strategy import Strategy
from cointrader.signals.CCISignal import CCISignal
from cointrader.signals.ADXSignal import ADXSignal

class ADX(Strategy):
    def __init__(self, symbol: str, name='adx_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.adx = ADXSignal(symbol=self._symbol, period=14, threshold=25)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.adx.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.adx.ready() and self.adx.above() and self.adx.cross_up():
            self._buy_signal_name = self.adx.name()
            return True
        return False

    def sell_signal(self):
        if self.adx.ready() and self.adx.below() and self.adx.cross_down():
            self._sell_signal_name = self.adx.name()
            return True
        return False
