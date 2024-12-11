from cointrader.common.Strategy import Strategy
from cointrader.signals.SAMASignal import SAMASignal

class SAMA(Strategy):
    def __init__(self, symbol: str, name='default'):
        super().__init__(symbol=symbol, name=name)
        self.sama = SAMASignal(symbol=self._symbol)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.sama.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.sama.ready() and self.sama.cross_up():
            self._buy_signal_name = self.sama.name()
            return True
        return False

    def sell_signal(self):
        if self.sama.ready() and self.sama.cross_down():
            self._sell_signal_name = self.sama.name()
            return True
        return False
