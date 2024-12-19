from cointrader.common.Strategy import Strategy
from cointrader.signals.MACDSignal import MACDSignal

class MACD(Strategy):
    def __init__(self, symbol: str, name='macd_strategy', granularity=0):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.macd = MACDSignal(symbol=self._symbol, short_period=12, long_period=26, signal_period=9)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.macd.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.macd.ready() and self.macd.cross_up():
            self._buy_signal_name = self.macd.name()
            return True
        return False

    def sell_signal(self):
        if self.macd.ready() and self.macd.cross_down():
            self._sell_signal_name = self.macd.name()
            return True
        return False
