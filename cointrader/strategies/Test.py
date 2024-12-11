from cointrader.common.Strategy import Strategy
from cointrader.signals.MACDSignal import MACDSignal
from cointrader.signals.RSISignal import RSISignal
from cointrader.signals.SAMASignal import SAMASignal
from cointrader.signals.ZLEMACross import ZLEMACross
from cointrader.signals.EMACross import EMACross
from cointrader.signals.SupertrendSignal import SupertrendSignal
from cointrader.signals.ADXSignal import ADXSignal

class Test(Strategy):
    def __init__(self, symbol: str, name='test'):
        super().__init__(symbol=symbol, name=name)
        self.macd = MACDSignal(symbol=self._symbol, short_period=12, long_period=26, signal_period=9)
        self.sama = SAMASignal(symbol=self._symbol)
        self.zlema = ZLEMACross(symbol=self._symbol, short_period=12, long_period=26)
        self.rsi = RSISignal(symbol=self._symbol, period=14, overbought=80, oversold=30)
        self.ema = EMACross(symbol=self._symbol, short_period=12, long_period=26)
        self.supertrend = SupertrendSignal(symbol=self._symbol, period=14, multiplier=3)
        self.adx = ADXSignal(symbol=self._symbol, period=14, threshold=20)
        self._buy_signal_name = None
        self._sell_signal_name = None

    def update(self, kline):
        self.macd.update(kline)
        self.sama.update(kline)
        self.zlema.update(kline)
        self.rsi.update(kline)
        self.ema.update(kline)
        self.supertrend.update(kline)
        self.adx.update(kline)

    def buy_signal_name(self):
        """
        Returns the name of the signal that triggered the buy signal.
        """
        result = self._buy_signal_name
        return result

    def sell_signal_name(self):
        """
        Returns the name of the signal that triggered the sell signal.
        """
        result = self._sell_signal_name
        return result

    def buy_signal(self):
        disable_buy = False
        buy = False
        if self.adx.ready() and self.adx.below():
            disable_buy = True
        if self.rsi.ready() and not self.rsi.below():
            disable_buy = True
        #if self.zlema.ready() and self.zlema.cross_up():
        #    return True
        if self.supertrend.ready() and self.supertrend.decreasing():
            disable_buy = True
        if self.supertrend.ready() and self.supertrend.cross_up():
            self._buy_signal_name = self.supertrend.name()
            buy = True
        if self.macd.ready() and self.macd.cross_up():
            self._buy_signal_name = self.macd.name()
            buy = True
        if self.ema.ready() and self.ema.cross_up():
            self._buy_signal_name = self.ema.name()
            buy = True
        if self.adx.ready() and self.adx.cross_up():
            self._buy_signal_name = self.adx.name()
            buy = True
        if self.sama.ready() and self.sama.cross_up():
            self._buy_signal_name = self.sama.name()
            buy = True

        if not disable_buy:
            return buy
        return False

    def sell_signal(self):
        disable_sell = False
        sell = False
        #if self.zlema.ready() and self.zlema.cross_down():
        #    return True
        #if self.supertrend.ready() and self.supertrend.decreasing():
        #    return True
        #if self.supertrend.ready() and self.supertrend.increasing():
        #    disable_sell = True
        if self.supertrend.ready() and self.supertrend.cross_down():
            if not sell:
                self._sell_signal_name = self.supertrend.name()
                sell = True
        #if self.macd.ready() and self.macd.cross_down():
        #    self._sell_signal_name = self.macd.name()
        #    sell = True
        if self.rsi.ready() and self.rsi.above():
            if not sell:
                self._sell_signal_name = self.rsi.name()
                sell = True
        if self.ema.ready() and self.ema.cross_down():
            if not sell:
                self._sell_signal_name = self.ema.name()
                #print(type(self.ema))
                sell = True
        if self.adx.ready() and self.adx.cross_down():
            if not sell:
                self._sell_signal_name = self.adx.name()
                sell = True
        if self.sama.ready() and self.sama.cross_down():
            if not sell:
                self._sell_signal_name = self.sama.name()
                sell = True

        if not disable_sell:
            return sell
        return False
