from cointrader.common.Strategy import Strategy
from cointrader.signals.EMACross import EMACross
from cointrader.signals.VWAPSignal import VWAPSignal

class VWAP(Strategy):
    def __init__(self, symbol: str, name='vwap'):
        super().__init__(symbol=symbol, name=name)
        self.vwap = VWAPSignal(symbol=self._symbol, period=14)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.vwap.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.vwap.ready() and self.vwap.cross_up():
            self._buy_signal_name = self.vwap.name()
            return True
        return False

    def sell_signal(self):
        if self.vwap.ready() and self.vwap.cross_down():
            self._sell_signal_name = self.vwap.name()
            return True
        return False
