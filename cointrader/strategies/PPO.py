from cointrader.common.Strategy import Strategy
from cointrader.signals.PPOSignal import PPOSignal

class PPO(Strategy):
    def __init__(self, symbol: str, name='ppo_strategy', granularity=0, weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self.ppo = PPOSignal(symbol=self._symbol, short_period=12, long_period=26, signal_period=9)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.ppo.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.ppo.ready() and self.ppo.cross_up():
            self._buy_signal_name = self.ppo.name()
            return True
        return False

    def sell_signal(self):
        if self.ppo.ready() and self.ppo.cross_down():
            self._sell_signal_name = self.ppo.name()
            return True
        return False
