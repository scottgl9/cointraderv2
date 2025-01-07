from cointrader.common.Strategy import Strategy
from cointrader.signals.SMACross import SMACross

class SMA(Strategy):
    def __init__(self, symbol: str, name='sma_cross', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.sma = SMACross(symbol=self._symbol, short_period=50, long_period=100)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.sma.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.sma.ready() and self.sma.cross_up():
            self._buy_signal_name = self.sma.name()
            return True
        return False

    def sell_signal(self):
        if self.sma.ready() and self.sma.cross_down():
            self._sell_signal_name = self.sma.name()
            if self._sell_signal_name is None:
                print(type(self.sma))
            return True
        return False
