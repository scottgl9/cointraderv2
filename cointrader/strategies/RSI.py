from cointrader.common.Strategy import Strategy
from cointrader.signals.RSISignal import RSISignal

class RSI(Strategy):
    def __init__(self, symbol: str, name='rsi_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.rsi = RSISignal(symbol=self._symbol, period=14, overbought=70, oversold=30)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.rsi.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.rsi.ready() and self.rsi.below():
            self._buy_signal_name = self.rsi.name()
            return True
        return False

    def sell_signal(self):
        if self.rsi.ready() and self.rsi.above():
            self._sell_signal_name = self.rsi.name()
            return True
        return False
