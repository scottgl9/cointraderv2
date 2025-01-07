from cointrader.common.Strategy import Strategy
from cointrader.signals.IchimokuSignal import IchimokuSignal

class Ichimoku(Strategy):
    def __init__(self, symbol: str, name='ichimoku_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.ichimoku = IchimokuSignal(symbol=self._symbol)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.ichimoku.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.ichimoku.ready() and self.ichimoku.cross_up():
            self._buy_signal_name = self.ichimoku.name()
            return True
        return False

    def sell_signal(self):
        if self.ichimoku.ready() and self.ichimoku.cross_down():
            self._sell_signal_name = self.ichimoku.name()
            return True
        return False
