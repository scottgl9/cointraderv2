from cointrader.common.Strategy import Strategy
from cointrader.signals.VOSignal import VOSignal

class VO(Strategy):
    def __init__(self, symbol: str, name='volume_oscillator_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.volume_oscillator = VOSignal(symbol=self._symbol, short_period=14, long_period=28, threshold=0)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.volume_oscillator.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.volume_oscillator.ready() and self.volume_oscillator.cross_up():
            self._buy_signal_name = self.volume_oscillator.name()
            return True
        return False

    def sell_signal(self):
        if self.volume_oscillator.ready() and self.volume_oscillator.cross_down():
            self._sell_signal_name = self.volume_oscillator.name()
            return True
        return False
