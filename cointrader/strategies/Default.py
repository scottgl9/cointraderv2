from cointrader.common.Strategy import Strategy
from cointrader.signals.MACDSignal import MACDSignal
from cointrader.signals.RSISignal import RSISignal
from cointrader.signals.SAMASignal import SAMASignal
from cointrader.signals.ZLEMACross import ZLEMACross
from cointrader.signals.EMACross import EMACross
from cointrader.signals.SupertrendSignal import SupertrendSignal
from cointrader.signals.SqueezeMomentumSignal import SqueezeMomentumSignal
from cointrader.signals.ADXSignal import ADXSignal
from cointrader.signals.ROCSignal import ROCSignal
from cointrader.signals.PSARSignal import PSARSignal
from cointrader.signals.VWAPSignal import VWAPSignal

class Default(Strategy):
    def __init__(self, symbol: str, name='default'):
        super().__init__(symbol=symbol, name=name)
        self.macd = MACDSignal(symbol=self._symbol, short_period=12, long_period=26, signal_period=9)
        self.sama = SAMASignal(symbol=self._symbol)
        self.zlema = ZLEMACross(symbol=self._symbol, short_period=12, long_period=26)
        self.rsi = RSISignal(symbol=self._symbol, period=14, overbought=80, oversold=30)
        self.ema = EMACross(symbol=self._symbol, short_period=12, long_period=26)
        self.supertrend = SupertrendSignal(symbol=self._symbol, period=14, multiplier=3)
        self.adx = ADXSignal(symbol=self._symbol, period=14, threshold=20)
        self.squeeze = SqueezeMomentumSignal(symbol=self._symbol, length=20, multBB=2.0, multKC=1.5)
        self.roc = ROCSignal(symbol=self._symbol, period=14)
        self.psar = PSARSignal(symbol=self._symbol, af=0.02, max_af=0.2)
        self.vwap = VWAPSignal(symbol=self._symbol, period=14)
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
        self.roc.update(kline)
        self.squeeze.update(kline)
        self.psar.update(kline)

    def buy_signal_name(self):
        result = self._buy_signal_name
        #self._buy_signal_name = None
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        #self._sell_signal_name = None
        return result

    def buy_signal(self):
        if self.vwap.ready() and self.vwap.below():
            return False
        # Buying: Momentum + trend confirmation
        if self.macd.ready() and self.rsi.ready() and self.supertrend.ready():
            if self.macd.cross_up() and self.rsi.below() and self.supertrend.cross_up():
                self._buy_signal_name = 'macd_rsi_supertrend'
                return True

        if self.ema.ready() and self.adx.ready():
            if self.ema.cross_up() and self.adx.above():
                self._buy_signal_name = 'ema_adx'
                return True
            
        if self.squeeze.ready() and self.psar.ready():
            if self.squeeze.cross_up() and self.psar.cross_up():
                self._buy_signal_name = 'squeeze_psar'
                return True
        
        # #if self.rsi.ready() and (self.rsi.decreasing() or self.rsi.above()):
        # #    return False
        # if self.adx.ready() and self.adx.below():#(self.adx.decreasing() or self.adx.below()):
        #     return False
        # if self.rsi.ready() and not self.rsi.below() and not self.rsi.decreasing():
        #     return False
        # #if self.zlema.ready() and self.zlema.cross_up():
        # #    return True
        # #if self.sama.ready() and self.sama.buy_signal():
        # if self.supertrend.ready() and self.supertrend.decreasing():
        #     return False
        # if self.supertrend.ready() and self.supertrend.cross_up():
        #     self._buy_signal_name = self.supertrend.name()
        #     return True
        # if self.squeeze.ready() and self.squeeze.cross_up():
        #     self._buy_signal_name = self.squeeze.name()
        #     return True
        # if self.macd.ready() and self.macd.cross_up():
        #     self._buy_signal_name = self.macd.name()
        #     return True
        # if self.ema.ready() and self.ema.cross_up():
        #     self._buy_signal_name = self.ema.name()
        #     return True
        # if self.adx.ready() and self.adx.cross_up():
        #     self._buy_signal_name = self.adx.name()
        #     return True
        # if self.sama.ready() and self.sama.cross_up():
        #     self._buy_signal_name = self.sama.name()
        #     return True
        # if self.roc.ready() and self.roc.cross_up():
        #     self._buy_signal_name = self.roc.name()
        #     return True
        # if self.psar.ready() and self.psar.cross_up():
        #     self._buy_signal_name = self.psar.name()
        #     return True
        return False

    def sell_signal(self):
        if self.vwap.ready() and self.vwap.above():
            return False
        # Selling: Momentum + trend confirmation
        if self.macd.ready() and self.rsi.ready() and self.supertrend.ready():
            if self.macd.cross_down() and self.rsi.above() and self.supertrend.cross_down():
                self._sell_signal_name = 'macd_rsi_supertrend'
                return True
            
        if self.ema.ready() and self.adx.ready():
            if self.ema.cross_down() and self.adx.below():
                self._sell_signal_name = 'ema_adx'
                return True
            
        if self.squeeze.ready() and self.psar.ready():
            if self.squeeze.cross_down() and self.psar.cross_down():
                self._sell_signal_name = 'squeeze_psar'
                return True

        #if self.zlema.ready() and self.zlema.cross_down():
        #    return True
        #if self.supertrend.ready() and self.supertrend.decreasing():
        #    return True
        # if self.supertrend.ready() and self.supertrend.cross_down():
        #     self._sell_signal_name = self.supertrend.name()
        #     return True
        # if self.macd.ready() and self.macd.cross_down():
        #     self._sell_signal_name = self.macd.name()
        #     return True
        # if self.rsi.ready() and self.rsi.above():
        #     self._sell_signal_name = self.rsi.name()
        #     return True
        # if self.ema.ready() and self.ema.cross_down():
        #     self._sell_signal_name = self.ema.name()
        #     return True
        # if self.adx.ready() and self.adx.cross_down():
        #     self._sell_signal_name = self.adx.name()
        #     return True
        # if self.sama.ready() and self.sama.cross_down():
        #     self._sell_signal_name = self.sama.name()
        #     return True
        # if self.squeeze.ready() and self.squeeze.cross_down():
        #     self._sell_signal_name = self.squeeze.name()
        #     return True
        # if self.roc.ready() and self.roc.cross_down():
        #     self._sell_signal_name = self.roc.name()
        #     return True
        # if self.psar.ready() and self.psar.cross_down():
        #     self._sell_signal_name = self.psar.name()
        #     return True
        return False
