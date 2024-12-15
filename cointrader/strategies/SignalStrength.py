# Just like TradingView buy, strong buy, neutral, strong sell, etc we will use the various signals to determine performing a buy or sell based on indicator consensus.
from cointrader.common.Strategy import Strategy
from cointrader.common.Signal import Signal
from cointrader.order.OrderSide import OrderSide
from cointrader.signals.MACDSignal import MACDSignal
from cointrader.signals.RSISignal import RSISignal
from cointrader.signals.SAMASignal import SAMASignal
from cointrader.signals.ZLEMACross import ZLEMACross
from cointrader.signals.EMACross import EMACross
from cointrader.signals.SMACross import SMACross
from cointrader.signals.SupertrendSignal import SupertrendSignal
from cointrader.signals.SqueezeMomentumSignal import SqueezeMomentumSignal
from cointrader.signals.ADXSignal import ADXSignal
from cointrader.signals.ROCSignal import ROCSignal
from cointrader.signals.PSARSignal import PSARSignal
from cointrader.signals.VWAPSignal import VWAPSignal

class SignalStrength(Strategy):
    def __init__(self, symbol: str, name='signal_strength'):
        super().__init__(symbol=symbol, name=name)
        self._buy_signal_name = None
        self._sell_signal_name = None
        super().__init__(symbol=symbol, name=name)

        self.signals: dict[str, Signal] = {}
        self.signals['macd'] = MACDSignal(symbol=self._symbol, short_period=12, long_period=26, signal_period=9)
        self.signals['sama'] = SAMASignal(symbol=self._symbol)
        self.signals['zlema'] = ZLEMACross(symbol=self._symbol, short_period=12, long_period=26)
        self.signals['rsi'] = RSISignal(symbol=self._symbol, period=14, overbought=70, oversold=30)
        self.signals['ema'] = EMACross(symbol=self._symbol, short_period=12, long_period=26)
        self.signals['sma'] = SMACross(symbol=self._symbol, short_period=50, long_period=100)
        self.signals['supertrend'] = SupertrendSignal(symbol=self._symbol, period=14, multiplier=3)
        self.signals['adx'] = ADXSignal(symbol=self._symbol, period=14, threshold=20)
        self.signals['squeeze'] = SqueezeMomentumSignal(symbol=self._symbol, length=20, multBB=2.0, multKC=1.5)
        self.signals['roc'] = ROCSignal(symbol=self._symbol, period=14)
        self.signals['psar'] = PSARSignal(symbol=self._symbol, af=0.02, max_af=0.2)
        self.signals['vwap'] = VWAPSignal(symbol=self._symbol, period=14)

        self.signal_states: dict[str, OrderSide] = {}
        for name in self.signals.keys():
            self.signal_states[name] = OrderSide.NONE

    def update(self, kline):
        for signal in self.signals.values():
            signal.update(kline)
        
        if self.signals['macd'].ready():
            if self.signals['macd'].cross_up():
                self.signal_states['macd'] = OrderSide.BUY
            elif self.signals['macd'].cross_down():
                self.signal_states['macd'] = OrderSide.SELL

        if self.signals['sama'].ready():
            if self.signals['sama'].cross_up():
                self.signal_states['sama'] = OrderSide.BUY
            elif self.signals['sama'].cross_down():
                self.signal_states['sama'] = OrderSide.SELL

        if self.signals['zlema'].ready():
            if self.signals['zlema'].cross_up():
                self.signal_states['zlema'] = OrderSide.BUY
            elif self.signals['zlema'].cross_down():
                self.signal_states['zlema'] = OrderSide.SELL

        if self.signals['rsi'].ready():
            if self.signals['rsi'].above():
                self.signal_states['rsi'] = OrderSide.SELL
            elif self.signals['rsi'].below():
                self.signal_states['rsi'] = OrderSide.BUY
            else:
                self.signal_states['rsi'] = OrderSide.NONE

        if self.signals['ema'].ready():
            if self.signals['ema'].cross_up():
                self.signal_states['ema'] = OrderSide.BUY
            elif self.signals['ema'].cross_down():
                self.signal_states['ema'] = OrderSide.SELL

        if self.signals['sma'].ready():
            if self.signals['sma'].cross_up():
                self.signal_states['sma'] = OrderSide.BUY
            elif self.signals['sma'].cross_down():
                self.signal_states['sma'] = OrderSide.SELL

        if self.signals['supertrend'].ready():
            if self.signals['supertrend'].cross_up():
                self.signal_states['supertrend'] = OrderSide.BUY
            elif self.signals['supertrend'].cross_down():
                self.signal_states['supertrend'] = OrderSide.SELL

        if self.signals['adx'].ready():
            if self.signals['adx'].above():
                if self.signals['adx'].cross_up():
                    self.signal_states['adx'] = OrderSide.BUY
                elif self.signals['adx'].cross_down():
                    self.signal_states['adx'] = OrderSide.SELL
            elif self.signals['adx'].below():
                self.signal_states['adx'] = OrderSide.NONE

        if self.signals['squeeze'].ready():
            if self.signals['squeeze'].cross_up():
                self.signal_states['squeeze'] = OrderSide.BUY
            elif self.signals['squeeze'].cross_down():
                self.signal_states['squeeze'] = OrderSide.SELL
        
        if self.signals['roc'].ready():
            if self.signals['roc'].cross_up():
                self.signal_states['roc'] = OrderSide.BUY
            elif self.signals['roc'].cross_down():
                self.signal_states['roc'] = OrderSide.SELL

        if self.signals['psar'].ready():
            if self.signals['psar'].cross_up():
                self.signal_states['psar'] = OrderSide.BUY
            elif self.signals['psar'].cross_down():
                self.signal_states['psar'] = OrderSide.SELL

        if self.signals['vwap'].ready():
            if self.signals['vwap'].above():
                self.signal_states['vwap'] = OrderSide.BUY
            elif self.signals['vwap'].below():
                self.signal_states['vwap'] = OrderSide.SELL

    def buy_signal_name(self):
        result = self._buy_signal_name
        return result

    def sell_signal_name(self):
        result = self._sell_signal_name
        return result

    def _count_signals(self):
        self._buy_signal_name = ""
        self._sell_signal_name = ""
        buy_signal_count = 0
        sell_signal_count = 0
        for name, state in self.signal_states.items():
            if state == OrderSide.BUY:
                buy_signal_count += 1
                self._buy_signal_name += name
            elif state == OrderSide.SELL:
                sell_signal_count += 1
                self._sell_signal_name += name
        return buy_signal_count, sell_signal_count

    def buy_signal(self):
        buy_signal_count, sell_signal_count = self._count_signals()
        if buy_signal_count > sell_signal_count:
            return True
        return False

    def sell_signal(self):
        buy_signal_count, sell_signal_count = self._count_signals()
        if sell_signal_count > buy_signal_count:
            return True
        return False
