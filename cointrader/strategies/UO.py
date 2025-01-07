from cointrader.common.Strategy import Strategy
from cointrader.signals.UltimateOscillatorSignal import UltimateOscillatorSignal

class UO(Strategy):
    def __init__(self, symbol: str, name='uo_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.uo = UltimateOscillatorSignal(symbol=self._symbol, short_period=7, medium_period=14, long_period=28)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.uo.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.uo.ready() and self.uo.cross_up():
            self._buy_signal_name = self.uo.name()
            return True
        return False

    def sell_signal(self):
        if self.uo.ready() and self.uo.cross_down():
            self._sell_signal_name = self.uo.name()
            return True
        return False
