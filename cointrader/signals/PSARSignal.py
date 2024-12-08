from cointrader.common.Signal import Signal
from cointrader.common.Kline import Kline
from cointrader.indicators.PSAR import PSAR  # Assuming PSAR is implemented as discussed

class PSARSignal(Signal):
    def __init__(self, name, symbol, af=0.02, max_af=0.2):
        super().__init__(name, symbol)
        self.af = af
        self.max_af = max_af
        self.psar = PSAR(af=self.af, max_af=self.max_af)
        self.reset()

    def reset(self):
        self.psar.reset()
        self._cross_up = False
        self._cross_down = False
        
        # Track previous trend or psar relative position to price
        # We'll store a boolean: psar_below = True if PSAR < price (bullish position)
        # psar_below = False if PSAR > price (bearish position)
        self.psar_below = None

    def update(self, kline: Kline):
        result = self.psar.update(kline)
        if result is None:
            return None

        current_psar = self.psar.get_last_value()
        current_price = kline.close

        # Determine current PSAR position relative to price
        current_psar_below = current_psar < current_price

        if self.psar_below is not None:
            # Check for flips
            # If previously psar was above price and now below price => bullish cross_up
            if self.psar_below == False and current_psar_below == True:
                self._cross_up = True

            # If previously psar was below price and now above price => bearish cross_down
            if self.psar_below == True and current_psar_below == False:
                self._cross_down = True

        # Update psar_below for next iteration
        self.psar_below = current_psar_below
        return result

    def ready(self):
        return self.psar.ready()

    def increasing(self):
        # PSAR typically moves in a known direction. 
        # We'll consider increasing if last psar value > previous psar value
        # For simplicity, let's just say if last two values show an increase.
        if len(self.psar.klines) < 2:
            return False
        # We need to store previous psar values for this logic:
        # One approach: we can track the last psar in update.
        # For now, let's just return False unless we store a deque.
        return False

    def decreasing(self):
        # Similar logic as increasing, would require tracking past psar values.
        return False

    def above(self):
        # PSAR above price?
        if self.psar.get_last_value() is None or self.psar.get_last_kline() is None:
            return False
        return self.psar.get_last_value() > self.psar.get_last_kline().close

    def below(self):
        # PSAR below price?
        if self.psar.get_last_value() is None or self.psar.get_last_kline() is None:
            return False
        return self.psar.get_last_value() < self.psar.get_last_kline().close

    def cross_up(self):
        # Returns True if psar just flipped below price
        result = self._cross_up
        self._cross_up = False
        return result

    def cross_down(self):
        # Returns True if psar just flipped above price
        result = self._cross_down
        self._cross_down = False
        return result
