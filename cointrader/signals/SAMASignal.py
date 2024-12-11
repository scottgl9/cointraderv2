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

        self.reset()

    def reset(self):
        # Reset the indicator and internal variables
        self.indicator.reset()
        #self._values = deque(maxlen=self.indicator.length)
        self._cross_up = False
        self._cross_down = False
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

        if self._longsignal:
            self._cross_down = True
        elif self._shortsignal:
            self._cross_up = True

    def increasing(self):
        return self._longsignal

    def decreasing(self):
        return self._shortsignal

    def cross_up(self):
        result = self._cross_up
        self._cross_up = False
        return result

    def cross_down(self):
        result = self._cross_down
        self._cross_down = False
        return result
    
    def ready(self):
        return self.indicator.ready()
