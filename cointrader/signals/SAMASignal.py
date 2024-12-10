from collections import deque
from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.SAMA import SlopeAdaptiveMovingAverage

class SAMASignal(Signal):
    def __init__(self, name='sama', symbol=None, **kwargs):
        super().__init__(name, symbol)
        # Initialize SAMAIndicator with parameters from kwargs or defaults
        self.indicator = SlopeAdaptiveMovingAverage(
            length=kwargs.get('length', 200),
            majLength=kwargs.get('majLength', 14),
            minLength=kwargs.get('minLength', 6),
            slopePeriod=kwargs.get('slopePeriod', 34),
            slopeInRange=kwargs.get('slopeInRange', 25),
            flat=kwargs.get('flat', 17)
        )
        # Cross detection
        self._last_up = False
        self._last_down = False

        # Buy/Sell signals
        self._longsignal = False
        self._shortsignal = False

        self.reset()

    def reset(self):
        # Reset the indicator and internal variables
        self.indicator.reset()
        #self._values = deque(maxlen=self.indicator.length)
        self._cross_up = False
        self._cross_down = False
        self._last_up = False
        self._last_down = False
        self._longsignal = False
        self._shortsignal = False

    def update(self, kline: Kline):
        # Update the indicator with the closing price
        result = self.indicator.update(kline)
        if not result:
            return
            #{
            #'ma': self.ma,
            #'slope': slope,
            #'longsignal': longsignal,
            #'shortsignal': shortsignal
            # }

        self._longsignal = result['longsignal']
        self._shortsignal = result['shortsignal']

    def increasing(self):
        return self._longsignal

    def decreasing(self):
        return self._shortsignal

    def buy_signal(self):
        return self._longsignal

    def sell_signal(self):
        return self._shortsignal
    
    def ready(self):
        return self.indicator.ready()
