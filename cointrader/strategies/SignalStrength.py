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
from cointrader.signals.IchimokuSignal import IchimokuSignal
from cointrader.signals.CMFSignal import CMFSignal
from cointrader.signals.DPOSignal import DPOSignal
from cointrader.signals.UltimateOscillatorSignal import UltimateOscillatorSignal
from cointrader.signals.AwesomeOscillatorSignal import AwesomeOscillatorSignal
from cointrader.signals.CCISignal import CCISignal
from cointrader.signals.VOSignal import VOSignal
from cointrader.signals.KVOSignal import KVOSignal
from cointrader.signals.EOMSignal import EOMSignal
from cointrader.signals.KSTSignal import KSTSignal

class SignalStrength(Strategy):
    def __init__(self, symbol: str, name='signal_strength', granularity=0, signal_weights=None):
        super().__init__(symbol=symbol, name=name, granularity=granularity)
        self._buy_signal_name = None
        self._sell_signal_name = None

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
                'cmf': 1.3,
                'cci': 1.3,
                'ao': 0,
                'uo': 0,
                'dpo': 0,
                'ichimoku': 0,
                'vo': 0,
                'kvo': 1.2,
                'eom': 0,
                'kst': 1.8,
                # minor signal weights
                'macd_change': 0.5,
                #'zlema_change': 0.2,
                'rsi_change': 0.5,
                'stoch_change': 0.5,
                #'ema_change': 0.3,
                'adx_change': 0.3,
                'roc_change': 0.5,
                'vwap_change': 0.5,
                'vo_change': 0,
                #'kvo_change': 0.5,
                #'uo_change': 0.3
                #'kst_change': 0.2
            }

        self._total_weight = sum(self._signal_weights.values())

        self.signals: dict[str, Signal] = {}
        if self._signal_weights['macd'] > 0:
            self.signals['macd'] = MACDSignal(symbol=self._symbol, short_period=12, long_period=26, signal_period=9)
        if self._signal_weights['sama'] > 0:
            self.signals['sama'] = SAMASignal(symbol=self._symbol)
        if self._signal_weights['zlema'] > 0:
            self.signals['zlema'] = ZLEMACross(symbol=self._symbol, short_period=12, long_period=26)
        if self._signal_weights['rsi'] > 0:
            self.signals['rsi'] = RSISignal(symbol=self._symbol, period=14, overbought=70, oversold=30)
        if self._signal_weights['stochastic'] > 0:
            self.signals['stochastic'] = StochasticSignal(symbol=self._symbol, k_period=14, d_period=3, overbought=80, oversold=20)
        if self._signal_weights['ema'] > 0:
            self.signals['ema'] = EMACross(symbol=self._symbol, short_period=12, long_period=26)
        if self._signal_weights['sma'] > 0:
            self.signals['sma'] = SMACross(symbol=self._symbol, short_period=50, long_period=100)
        if self._signal_weights['supertrend'] > 0:
            self.signals['supertrend'] = SupertrendSignal(symbol=self._symbol, period=14, multiplier=3)
        if self._signal_weights['adx'] > 0:
            self.signals['adx'] = ADXSignal(symbol=self._symbol, period=14, threshold=20)
        if self._signal_weights['squeeze'] > 0:
            self.signals['squeeze'] = SqueezeMomentumSignal(symbol=self._symbol, length=20, multBB=2.0, multKC=1.5)
        if self._signal_weights['roc'] > 0:
            self.signals['roc'] = ROCSignal(symbol=self._symbol, period=14)
        if self._signal_weights['psar'] > 0:
            self.signals['psar'] = PSARSignal(symbol=self._symbol, af=0.02, max_af=0.2)
        if self._signal_weights['vwap'] > 0:   
            self.signals['vwap'] = VWAPSignal(symbol=self._symbol, period=14)
        if self._signal_weights['ppo'] > 0:
            self.signals['ppo'] = PPOSignal(symbol=self._symbol, short_period=12, long_period=26, signal_period=9, overbought=100, oversold=-100)
        if self._signal_weights['cmf'] > 0:
            self.signals['cmf'] = CMFSignal(symbol=self._symbol, period=20, signal_period=9, overbought=0.05, oversold=-0.05)
        if self._signal_weights['cci'] > 0:
            self.signals['cci'] = CCISignal(symbol=self._symbol, period=20, overbought=100, oversold=-100)
        if self._signal_weights['ao'] > 0:
            self.signals['ao'] = AwesomeOscillatorSignal(symbol=self._symbol, short_period=5, long_period=34)
        if self._signal_weights['dpo'] > 0:
            self.signals['dpo'] = DPOSignal(symbol=self._symbol, period=20, overbought=50, oversold=-50)
        if self._signal_weights['uo'] > 0:
            self.signals['uo'] = UltimateOscillatorSignal(symbol=self._symbol, short_period=7, medium_period=14, long_period=28, overbought=70, oversold=30)
        if self._signal_weights['ichimoku'] > 0:
            self.signals['ichimoku'] = IchimokuSignal(symbol=self._symbol, win_short=9, win_med=26, win_long=52)
        if self._signal_weights['vo'] > 0:
            self.signals['vo'] = VOSignal(symbol=self._symbol, short_period=14, long_period=28, threshold=0.0)
        if self._signal_weights['kvo'] > 0:
            self.signals['kvo'] = KVOSignal(symbol=self._symbol, short_period=34, long_period=55, signal_period=13, threshold=0.0)
        if self._signal_weights['eom'] > 0:
            self.signals['eom'] = EOMSignal(symbol=self._symbol, period=14, threshold=0.0)
        if self._signal_weights['kst'] > 0:
            self.signals['kst'] = KSTSignal(symbol=self._symbol, roc_periods=[10, 15, 20, 30], smoothing_periods=[10, 10, 10, 15], weights=[1, 2, 3, 4], signal_period=9, threshold=0.0)

        self.signal_states: dict[str, OrderSide] = {}
        for name in self.signals.keys():
            self.signal_states[name] = OrderSide.NONE

    def update(self, kline):
        for name, signal in self.signals.items():
            if self._signal_weights[name] == 0:
                continue
            signal.update(kline)

        if self._signal_weights['macd'] > 0 and self.signals['macd'].ready():
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

        if self._signal_weights['sama'] > 0 and self.signals['sama'].ready():
            if self.signals['sama'].cross_up():
                self.signal_states['sama'] = OrderSide.BUY
            elif self.signals['sama'].cross_down():
                self.signal_states['sama'] = OrderSide.SELL

        if self._signal_weights['zlema'] > 0 and self.signals['zlema'].ready():
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

        if self._signal_weights['rsi'] > 0 and self.signals['rsi'].ready():
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

        if self._signal_weights['stochastic'] > 0 and self.signals['stochastic'].ready():
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

        if self._signal_weights['ema'] > 0 and self.signals['ema'].ready():
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

        if self._signal_weights['sma'] > 0 and self.signals['sma'].ready():
            if self.signals['sma'].cross_up():
                self.signal_states['sma'] = OrderSide.BUY
            elif self.signals['sma'].cross_down():
                self.signal_states['sma'] = OrderSide.SELL

        if self._signal_weights['supertrend'] > 0 and self.signals['supertrend'].ready():
            if self.signals['supertrend'].cross_up():
                self.signal_states['supertrend'] = OrderSide.BUY
            elif self.signals['supertrend'].cross_down():
                self.signal_states['supertrend'] = OrderSide.SELL

        if self._signal_weights['adx'] > 0 and self.signals['adx'].ready():
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

        if self._signal_weights['squeeze'] > 0 and self.signals['squeeze'].ready():
            if self.signals['squeeze'].cross_up():
                self.signal_states['squeeze'] = OrderSide.BUY
            elif self.signals['squeeze'].cross_down():
                self.signal_states['squeeze'] = OrderSide.SELL
        
        if self._signal_weights['roc'] > 0 and self.signals['roc'].ready():
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

        if self._signal_weights['psar'] > 0 and self.signals['psar'].ready():
            if self.signals['psar'].cross_up():
                self.signal_states['psar'] = OrderSide.BUY
            elif self.signals['psar'].cross_down():
                self.signal_states['psar'] = OrderSide.SELL

        if self._signal_weights['vwap'] > 0 and self.signals['vwap'].ready():
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

        if self._signal_weights['ppo'] > 0 and self.signals['ppo'].ready():
            if self.signals['ppo'].cross_up():
                self.signal_states['ppo'] = OrderSide.BUY
            elif self.signals['ppo'].cross_down():
                self.signal_states['ppo'] = OrderSide.SELL
        
        if self._signal_weights['cmf'] > 0 and self.signals['cmf'].ready():
           if self.signals['cmf'].cross_up():
               self.signal_states['cmf'] = OrderSide.BUY
           elif self.signals['cmf'].cross_down():
               self.signal_states['cmf'] = OrderSide.SELL  

        if self._signal_weights['cci'] > 0 and self.signals['cci'].ready():
            if self.signals['cci'].above():
                self.signal_states['cci'] = OrderSide.SELL
            elif self.signals['cci'].below():
                self.signal_states['cci'] = OrderSide.BUY
            else:
                self.signal_states['cci'] = OrderSide.NONE

        if self._signal_weights['ao'] > 0 and self.signals['ao'].ready():
            if self.signals['ao'].cross_up():
                self.signal_states['ao'] = OrderSide.BUY
            elif self.signals['ao'].cross_down():
                self.signal_states['ao'] = OrderSide.SELL

        if self._signal_weights['uo'] > 0 and self.signals['uo'].ready():
            if self.signals['uo'].above():
                self.signal_states['uo'] = OrderSide.SELL
            elif self.signals['uo'].below():
                self.signal_states['uo'] = OrderSide.BUY
            else:
                self.signal_states['uo'] = OrderSide.NONE
            if self.signals['uo'].increasing():
               if 'uo_change' in self._signal_weights.keys():
                   self.signal_states['uo_change'] = OrderSide.BUY
            elif self.signals['uo'].decreasing():
               if 'uo_change' in self._signal_weights.keys():
                   self.signal_states['uo_change'] = OrderSide.SELL
            else:
               if 'uo_change' in self._signal_weights.keys():
                   self.signal_states['uo_change'] = OrderSide.NONE

        if self._signal_weights['dpo'] > 0 and self.signals['dpo'].ready():
          if self.signals['dpo'].cross_up():
              self.signal_states['dpo'] = OrderSide.BUY
          elif self.signals['dpo'].cross_down():
              self.signal_states['dpo'] = OrderSide.SELL  

        if self._signal_weights['ichimoku'] > 0 and self.signals['ichimoku'].ready():
           if self.signals['ichimoku'].cross_up():
               self.signal_states['ichimoku'] = OrderSide.BUY
           elif self.signals['ichimoku'].cross_down():
               self.signal_states['ichimoku'] = OrderSide.SELL

        if self._signal_weights['vo'] > 0 and self.signals['vo'].ready():
            if self.signals['vo'].cross_up():
                self.signal_states['vo'] = OrderSide.BUY
            elif self.signals['vo'].cross_down():
                self.signal_states['vo'] = OrderSide.SELL
            if self.signals['vo'].increasing():
               if 'vo_change' in self._signal_weights.keys():
                   self.signal_states['vo_change'] = OrderSide.BUY
            elif self.signals['vo'].decreasing():
               if 'vo_change' in self._signal_weights.keys():
                   self.signal_states['vo_change'] = OrderSide.SELL
            else:
               if 'vo_change' in self._signal_weights.keys():
                   self.signal_states['vo_change'] = OrderSide.NONE
        
        if self._signal_weights['kvo'] > 0 and self.signals['kvo'].ready():
            if self.signals['kvo'].cross_up():
                self.signal_states['kvo'] = OrderSide.BUY
            elif self.signals['kvo'].cross_down():
                self.signal_states['kvo'] = OrderSide.SELL
            if self.signals['kvo'].increasing():
               if 'kvo_change' in self._signal_weights.keys():
                   self.signal_states['kvo_change'] = OrderSide.BUY
            elif self.signals['kvo'].decreasing():
               if 'kvo_change' in self._signal_weights.keys():
                   self.signal_states['kvo_change'] = OrderSide.SELL
            else:
               if 'kvo_change' in self._signal_weights.keys():
                   self.signal_states['kvo_change'] = OrderSide.NONE
        
        if self._signal_weights['eom'] > 0 and self.signals['eom'].ready():
            if self.signals['eom'].cross_up():
                self.signal_states['eom'] = OrderSide.BUY
            elif self.signals['eom'].cross_down():
                self.signal_states['eom'] = OrderSide.SELL

        if self._signal_weights['kst'] > 0 and self.signals['kst'].ready():
            if self.signals['kst'].cross_up():
                self.signal_states['kst'] = OrderSide.BUY
            elif self.signals['kst'].cross_down():
                self.signal_states['kst'] = OrderSide.SELL
            if self.signals['kst'].increasing():
               if 'kst_change' in self._signal_weights.keys():
                   self.signal_states['kst_change'] = OrderSide.BUY
            elif self.signals['kst'].decreasing():
               if 'kst_change' in self._signal_weights.keys():
                   self.signal_states['kst_change'] = OrderSide.SELL
            else:
               if 'kst_change' in self._signal_weights.keys():
                   self.signal_states['kst_change'] = OrderSide.NONE

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