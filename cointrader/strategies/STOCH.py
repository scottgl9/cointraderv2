from cointrader.common.Strategy import Strategy
from cointrader.signals.StochasticSignal import StochasticSignal

class STOCH(Strategy):
    def __init__(self, symbol: str, name='stoch_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.stoch = StochasticSignal(symbol=self._symbol, k_period=14, d_period=3, smooth=3)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.stoch.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.stoch.ready() and self.stoch.cross_up():
            self._buy_signal_name = self.stoch.name()
            return True
        return False

    def sell_signal(self):
        if self.stoch.ready() and self.stoch.cross_down():
            self._sell_signal_name = self.stoch.name()
            return True
        return False
