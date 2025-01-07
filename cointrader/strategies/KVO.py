from cointrader.common.Strategy import Strategy
from cointrader.signals.KVOSignal import KVOSignal

class KVO(Strategy):
    def __init__(self, symbol: str, name='kvo_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.kvo = KVOSignal(symbol=self._symbol, short_period=34, long_period=55, signal_period=13)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.kvo.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.kvo.ready() and self.kvo.cross_up():
            self._buy_signal_name = self.kvo.name()
            return True
        return False

    def sell_signal(self):
        if self.kvo.ready() and self.kvo.cross_down():
            self._sell_signal_name = self.kvo.name()
            return True
        return False
