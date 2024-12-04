from cointrader.common.Strategy import Strategy
from cointrader.signals.MACDSignal import MACDSignal
from cointrader.signals.RSISignal import RSISignal
from cointrader.signals.SAMASignal import SAMASignal

class Default(Strategy):
    def __init__(self, symbol: str, name='default'):
        super().__init__(symbol=symbol, name=name)
        self.macd = MACDSignal('macd', self._symbol, 12, 26, 9)
        self.sama = SAMASignal('sama', self._symbol)
        self.rsi = RSISignal(14, 70, 30)

    def update(self, kline):
        self.macd.update(kline)
        self.sama.update(kline)

    def buy(self):
        if self.rsi.ready() and self.rsi.decreasing():
            return False
        if self.sama.ready() and self.sama.buy_signal():
            if self.macd.ready() and self.macd.cross_up():
                return True
        return False

    def sell(self):
        if self.macd.ready() and self.macd.cross_down():
            return True
        if self.sama.ready() and self.sama.sell_signal():
            return True
        return False
