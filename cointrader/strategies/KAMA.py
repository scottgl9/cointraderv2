from cointrader.common.Strategy import Strategy
from cointrader.signals.KAMACross import KAMACross

class KAMA(Strategy):
    def __init__(self, symbol: str, name='kama_cross', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.kama = KAMACross(symbol=self._symbol, short_period=12, long_period=26)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.kama.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.kama.ready() and self.kama.cross_up():
            self._buy_signal_name = self.kama.name()
            return True
        return False

    def sell_signal(self):
        if self.kama.ready() and self.kama.cross_down():
            self._sell_signal_name = self.kama.name()
            return True
        return False
