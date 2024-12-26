from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.PPO import PPO

class PPOSignal(Signal):
    def __init__(self, name='ppo', symbol=None, short_period=12, long_period=26, signal_period=9, overbought=100, oversold=-100):
        """
        Initialize the PPO Signal.
        
        :param name: Name of the signal.
        :param symbol: Trading symbol.
        :param short_period: Short-term EMA period for PPO.
        :param long_period: Long-term EMA period for PPO.
        :param signal_period: Period for the signal line EMA.
        :param overbought: Threshold for overbought condition.
        :param oversold: Threshold for oversold condition.
        """
        super().__init__(name, symbol)
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period
        self.overbought = overbought
        self.oversold = oversold

        # Initialize PPO indicator
        self.ppo = PPO(name='ppo_indicator', short_period=self.short_period, long_period=self.long_period, signal_period=self.signal_period)
        self.reset()

    def reset(self):
        """
        Reset the PPO Signal to its initial state.
        """
        self.ppo.reset()
        self._cross_up = False
        self._cross_down = False
        self.ppo_values = deque(maxlen=2)  # To track previous and current PPO for cross detection

    def update(self, kline: Kline):
        """
        Update the PPO Signal with a new Kline and generate signals.
        
        :param kline: The new Kline data.
        :return: Signal action ('buy', 'sell', or None).
        """
        result = self.ppo.update(kline)
        if result is None:
            return None

        ppo = result['ppo']
        signal = result['signal']
        histogram = result['histogram']

        # Append current PPO value for crossover detection
        self.ppo_values.append(ppo)

        # Need at least two PPO values to detect a cross
        if len(self.ppo_values) < 2:
            return None

        prev_ppo = self.ppo_values[-2]
        current_ppo = self.ppo_values[-1]

        # Detect cross_up: PPO crosses above the signal line
        # Condition: previously PPO <= Signal, now PPO > Signal
        if prev_ppo <= signal and current_ppo > signal:
            self._cross_up = True

        # Detect cross_down: PPO crosses below the signal line
        # Condition: previously PPO >= Signal, now PPO < Signal
        if prev_ppo >= signal and current_ppo < signal:
            self._cross_down = True

        signal_action = None

        if self._cross_up:
            # Optional: Check if PPO is below oversold threshold for added confirmation
            if ppo < self.oversold:
                signal_action = 'buy'
            self._cross_up = False

        if self._cross_down:
            # Optional: Check if PPO is above overbought threshold for added confirmation
            if ppo > self.overbought:
                signal_action = 'sell'
            self._cross_down = False

        return signal_action

    def cross_up(self):
        return self._cross_up
    
    def cross_down(self):
        return self._cross_down

    def ready(self):
        """
        Check if the PPO Signal is ready to provide trading actions.
        
        :return: True if ready, False otherwise.
        """
        return self.ppo.ready()

    def get_last_value(self):
        """
        Get the latest PPO values.
        
        :return: A dictionary with 'ppo', 'signal', and 'histogram' or None.
        """
        return self.ppo.get_last_value()
