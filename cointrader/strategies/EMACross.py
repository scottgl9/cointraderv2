from cointrader.common.Strategy import Strategy
from cointrader.signals.EMACross import EMACross

class EMACross(Strategy):
    def __init__(self, symbol: str, name='ema_cross'):
        super().__init__(symbol=symbol, name=name)
        self.ema = EMACross(symbol=self._symbol, short_period=12, long_period=26)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.ema.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.ema.ready() and self.ema.cross_up():
            self._buy_signal_name = self.ema.name()
            return True
        return False

    def sell_signal(self):
        if self.ema.ready() and self.ema.cross_down():
            self._sell_signal_name = self.ema.name()
            if self._sell_signal_name is None:
                print(type(self.ema))
            return True
        return False
