from cointrader.common.Strategy import Strategy
from cointrader.signals.ZLEMACross import ZLEMACross

class ZLEMA(Strategy):
    def __init__(self, symbol: str, name='zlema_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.zlema = ZLEMACross(symbol=self._symbol, short_period=12, long_period=24)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.zlema.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.zlema.ready() and self.zlema.cross_up():
            self._buy_signal_name = self.zlema.name()
            return True
        return False

    def sell_signal(self):
        if self.zlema.ready() and self.zlema.cross_down():
            self._sell_signal_name = self.zlema.name()
            return True
        return False
