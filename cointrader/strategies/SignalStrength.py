# Just like TradingView buy, strong buy, neutral, strong sell, etc we will use the various signals to determine performing a buy or sell based on indicator consensus.
from cointrader.common.Strategy import Strategy
from cointrader.common.Signal import Signal
from cointrader.order.enum.OrderSide import OrderSide
from cointrader.signals.MACDSignal import MACDSignal
from cointrader.signals.RSISignal import RSISignal
from cointrader.signals.StochasticSignal import StochasticSignal
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
from cointrader.signals.PPOSignal import PPOSignal

class SignalStrength(Strategy):
    def __init__(self, symbol: str, name='signal_strength', granularity=0, signal_weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self._buy_signal_name = None
        self._sell_signal_name = None

        self.signals: dict[str, Signal] = {}
        self.signals['macd'] = MACDSignal(symbol=self._symbol, short_period=12, long_period=26, signal_period=9)
        self.signals['sama'] = SAMASignal(symbol=self._symbol)
        self.signals['zlema'] = ZLEMACross(symbol=self._symbol, short_period=12, long_period=26)
        self.signals['rsi'] = RSISignal(symbol=self._symbol, period=14, overbought=70, oversold=30)
        self.signals['stochastic'] = StochasticSignal(symbol=self._symbol, k_period=14, d_period=3, overbought=80, oversold=20)
        self.signals['ema'] = EMACross(symbol=self._symbol, short_period=12, long_period=26)
        self.signals['sma'] = SMACross(symbol=self._symbol, short_period=50, long_period=100)
        self.signals['supertrend'] = SupertrendSignal(symbol=self._symbol, period=14, multiplier=3)
        self.signals['adx'] = ADXSignal(symbol=self._symbol, period=14, threshold=20)
        self.signals['squeeze'] = SqueezeMomentumSignal(symbol=self._symbol, length=20, multBB=2.0, multKC=1.5)
        self.signals['roc'] = ROCSignal(symbol=self._symbol, period=14)
        self.signals['psar'] = PSARSignal(symbol=self._symbol, af=0.02, max_af=0.2)
        self.signals['vwap'] = VWAPSignal(symbol=self._symbol, period=14)
        self.signals['ppo'] = PPOSignal(symbol=self._symbol, short_period=12, long_period=26, signal_period=9, overbought=100, oversold=-100)

        if signal_weights is not None:
            self._signal_weights = signal_weights
        else:
            self._signal_weights = {
                'macd': 1.5,
                'sama': 1.0,
                'zlema': 1.2,
                'rsi': 1.3,
                'stochastic': 1.3,
                'ema': 1.1,
                'sma': 1.0,
                'supertrend': 1.4,
                'adx': 1.3,
                'squeeze': 1.2,
                'roc': 1.0,
                'psar': 1.1,
                'vwap': 1.2,
                'ppo': 1.1,
                # minor signal weights
                'macd_change': 0.5,
                #'zlema_change': 0.2,
                'rsi_change': 0.5,
                'stoch_change': 0.5,
                #'ema_change': 0.3,
                'adx_change': 0.3,
                'roc_change': 0.5,
                'vwap_change': 0.5
            }

        self._total_weight = sum(self._signal_weights.values())

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
            if self.signals['macd'].increasing():
                if 'macd_change' in self._signal_weights.keys():
                    self._signal_weights['macd_change'] = OrderSide.BUY
            elif self.signals['macd'].decreasing():
                if 'macd_change' in self._signal_weights.keys():
                    self._signal_weights['macd_change'] = OrderSide.SELL
            else:
                if 'macd_change' in self._signal_weights.keys():
                    self._signal_weights['macd_change'] = OrderSide.NONE

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
            #if self.signals['zlema'].increasing():
            #    self.signal_states['zlema_change'] = OrderSide.BUY
            #elif self.signals['zlema'].decreasing():
            #    self.signal_states['zlema_change'] = OrderSide.SELL
            #else:
            #    self.signal_states['zlema_change'] = OrderSide.NONE

        if self.signals['rsi'].ready():
            if self.signals['rsi'].above():
                self.signal_states['rsi'] = OrderSide.SELL
            elif self.signals['rsi'].below():
                self.signal_states['rsi'] = OrderSide.BUY
            else:
                self.signal_states['rsi'] = OrderSide.NONE
            if self.signals['rsi'].increasing():
                if 'rsi_change' in self._signal_weights.keys():
                    self.signal_states['rsi_change'] = OrderSide.BUY
            elif self.signals['rsi'].decreasing():
                if 'rsi_change' in self._signal_weights.keys():
                    self.signal_states['rsi_change'] = OrderSide.SELL
            else:
                if 'rsi_change' in self._signal_weights.keys():
                    self.signal_states['rsi_change'] = OrderSide.NONE

        if self.signals['stochastic'].ready():
            if self.signals['stochastic'].cross_up():
                self.signal_states['stochastic'] = OrderSide.BUY
            elif self.signals['stochastic'].cross_down():
                self.signal_states['stochastic'] = OrderSide.SELL
            if self.signals['stochastic'].increasing():
                if 'stoch_change' in self._signal_weights.keys():
                    self.signal_states['stoch_change'] = OrderSide.BUY
            elif self.signals['stochastic'].decreasing():
                if 'stoch_change' in self._signal_weights.keys():
                    self.signal_states['stoch_change'] = OrderSide.SELL
            else:
                if 'stoch_change' in self._signal_weights.keys():
                    self.signal_states['stoch_change'] = OrderSide.NONE

        if self.signals['ema'].ready():
            if self.signals['ema'].cross_up():
                self.signal_states['ema'] = OrderSide.BUY
            elif self.signals['ema'].cross_down():
                self.signal_states['ema'] = OrderSide.SELL
            #if self.signals['ema'].increasing():
            #    self.signal_states['ema_change'] = OrderSide.BUY
            #elif self.signals['ema'].decreasing():
            #    self.signal_states['ema_change'] = OrderSide.SELL
            #else:
            #    self.signal_states['ema_change'] = OrderSide.NONE

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
            if self.signals['adx'].increasing():
                if 'adx_change' in self._signal_weights.keys():
                    self.signal_states['adx_change'] = OrderSide.BUY
            elif self.signals['adx'].decreasing():
                if 'adx_change' in self._signal_weights.keys():
                    self.signal_states['adx_change'] = OrderSide.SELL
            else:
                if 'adx_change' in self._signal_weights.keys():
                    self.signal_states['adx_change'] = OrderSide.NONE

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
            if self.signals['roc'].increasing():
                if 'roc_change' in self._signal_weights.keys():
                    self.signal_states['roc_change'] = OrderSide.BUY
            elif self.signals['roc'].decreasing():
                if 'roc_change' in self._signal_weights.keys():
                    self.signal_states['roc_change'] = OrderSide.BUY
            else:
                if 'roc_change' in self._signal_weights.keys():
                    self.signal_states['roc_change'] = OrderSide.NONE

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
            if self.signals['vwap'].increasing():
                self.signal_states['vwap_change'] = OrderSide.BUY
            elif self.signals['vwap'].decreasing():
                self.signal_states['vwap_change'] = OrderSide.SELL
            else:
                self.signal_states['vwap_change'] = OrderSide.NONE

        if self.signals['ppo'].ready():
            if self.signals['ppo'].cross_up():
                self.signal_states['ppo'] = OrderSide.BUY
            elif self.signals['ppo'].cross_down():
                self.signal_states['ppo'] = OrderSide.SELL

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

    def _weighted_count_signals(self):
        self._buy_signal_name = ""
        self._sell_signal_name = ""
        buy_signal_weight = 0
        sell_signal_weight = 0

        for name, state in self.signal_states.items():
            weight = self._signal_weights.get(name, 1.0)
            if state == OrderSide.BUY:
                buy_signal_weight += weight
                self._buy_signal_name += name
            elif state == OrderSide.SELL:
                sell_signal_weight += weight
                self._sell_signal_name += name
        return buy_signal_weight, sell_signal_weight

    def buy_signal(self):
        buy_signal_weight, sell_signal_weight = self._weighted_count_signals()
        if buy_signal_weight == 0 or sell_signal_weight == 0:
            return False
        # make sure we have enough signals to make a decision
        if buy_signal_weight + sell_signal_weight < self._total_weight / 2:
            return False
        if buy_signal_weight > sell_signal_weight:
            return True
        return False

    def sell_signal(self):
        buy_signal_weight, sell_signal_weight = self._weighted_count_signals()
        if buy_signal_weight == 0 or sell_signal_weight == 0:
            return False
        # make sure we have enough signals to make a decision
        if buy_signal_weight + sell_signal_weight < self._total_weight / 2:
            return False
        if sell_signal_weight > buy_signal_weight:
            return True
        return False

    def strong_buy_signal(self):
        buy_signal_weight, sell_signal_weight = self._weighted_count_signals()
        if buy_signal_weight == 0 or sell_signal_weight == 0:
            return False
        # make sure we have enough signals to make a decision
        if buy_signal_weight + sell_signal_weight < self._total_weight / 2:
            return False
        if buy_signal_weight >= 2.0 * sell_signal_weight:
            return True
        return False

    def strong_sell_signal(self):
        buy_signal_weight, sell_signal_weight = self._weighted_count_signals()
        if buy_signal_weight == 0 or sell_signal_weight == 0:
            return False
        # make sure we have enough signals to make a decision
        if buy_signal_weight + sell_signal_weight < self._total_weight / 2:
            return False
        if sell_signal_weight >= 2.0 * buy_signal_weight:
            return True
        return False