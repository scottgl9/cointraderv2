from cointrader.common.Strategy import Strategy
from cointrader.signals.MACDSignal import MACDSignal
from cointrader.signals.RSISignal import RSISignal
from cointrader.signals.SAMASignal import SAMASignal
from cointrader.signals.ZLEMACross import ZLEMACross
from cointrader.signals.EMACross import EMACross
from cointrader.signals.SupertrendSignal import SupertrendSignal

class Default(Strategy):
    def __init__(self, symbol: str, name='default'):
        super().__init__(symbol=symbol, name=name)
        self.macd = MACDSignal('macd', self._symbol, 12, 26, 9)
        self.sama = SAMASignal('sama', self._symbol)
        self.zlema = ZLEMACross('zlema', self._symbol, 12, 26)
        self.rsi = RSISignal(14, 80, 30)
        self.ema = EMACross('ema', self._symbol, 12, 26)
        self.ema2 = EMACross('ema2', self._symbol, 6, 12)
        self.supertrend = SupertrendSignal('supertrend', self._symbol, period=14, multiplier=3)

    def update(self, kline):
        self.macd.update(kline)
        self.sama.update(kline)
        self.zlema.update(kline)
        self.rsi.update(kline)
        self.ema.update(kline)
        self.ema2.update(kline)
        self.supertrend.update(kline)

    def buy(self):
        #if self.rsi.ready() and (self.rsi.decreasing() or self.rsi.above()):
        #    return False
        if self.rsi.ready() and (not self.rsi.below()):# and self.rsi.decreasing()):
            return False
        #if self.zlema.ready() and self.zlema.cross_up():
        #    return True
        #if self.sama.ready() and self.sama.buy_signal():
        if self.supertrend.ready() and self.supertrend.decreasing():
            return False
        if self.supertrend.ready() and self.supertrend.cross_up():
            return True
        #if self.macd.ready() and self.macd.cross_up():
        #    return True
        if self.ema.ready() and self.ema.cross_up():
            return True
        return False

    def sell(self):
        #if self.zlema.ready() and self.zlema.cross_down():
        #    return True
        #if self.supertrend.ready() and self.supertrend.decreasing():
        #    return True
        if self.supertrend.ready() and self.supertrend.cross_down():
            return True
        #if self.macd.ready() and self.macd.cross_down():
        #    return True
        #if self.rsi.ready() and self.rsi.above():
        #    return True
        if self.ema.ready() and self.ema.cross_down():
            return True
        #if self.ema2.ready() and self.ema2.cross_down():
        #    return True
        #if self.sama.ready() and self.sama.sell_signal():
        #    return True
        return False
