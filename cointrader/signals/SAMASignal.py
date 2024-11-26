from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.SAMA import SlopeAdaptiveMovingAverage

class SAMASignal(Signal):
    def __init__(self, name, symbol, **kwargs):
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

    def reset(self):
        # Reset the indicator and internal variables
        self.indicator.reset()
        self._values.clear()
        self._cross_up = False
        self._cross_down = False
        self._last_up = False
        self._last_down = False
        self._longsignal = False
        self._shortsignal = False

    def update(self, kline: Kline):
        # Update the indicator with the closing price
        src = kline.close
        result = self.indicator.update(src)
        if not result:
            return

        ma = result['ma']
        slope = result['slope']

        # Determine trend direction
        up = slope >= self.indicator.flat
        down = slope <= -self.indicator.flat

        # Detect cross up and cross down
        if self.indicator.ready():
            prev_up = self._last_up
            prev_down = self._last_down
            self._cross_up = up and not prev_up
            self._cross_down = down and not prev_down
        else:
            self._cross_up = False
            self._cross_down = False

        self._last_up = up
        self._last_down = down

        # Generate swing state and signals
        prev_swing = self.indicator.swing
        if self._cross_up and self.indicator.swing <= 0:
            self.indicator.swing = 1
        elif self._cross_down and self.indicator.swing >= 0:
            self.indicator.swing = -1

        self._longsignal = self.indicator.swing == 1 and prev_swing != 1
        self._shortsignal = self.indicator.swing == -1 and prev_swing != -1

        # Store the current value
        self._values.append({
            'ma': ma,
            'slope': slope,
            'longsignal': self._longsignal,
            'shortsignal': self._shortsignal,
            'swing': self.indicator.swing
        })

    def ready(self):
        # The signal is ready when the indicator is ready
        return self.indicator.ready()

    def cross_up(self):
        return self._cross_up

    def cross_down(self):
        return self._cross_down

    def above(self):
        # Check if the price is above the moving average
        if self.indicator.ma is not None and len(self.indicator.src_history) > 0:
            return self.indicator.src_history[-1] > self.indicator.ma
        return False

    def below(self):
        # Check if the price is below the moving average
        if self.indicator.ma is not None and len(self.indicator.src_history) > 0:
            return self.indicator.src_history[-1] < self.indicator.ma
        return False

    def buy_signal(self):
        return self._longsignal

    def sell_signal(self):
        return self._shortsignal
