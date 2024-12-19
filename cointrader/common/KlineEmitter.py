# This class tracks klines with a certain granularity, and emits them with a larger granularity is met
from .Kline import Kline
from collections import deque

class KlineEmitter(object):
    def __init__(self, src_granularity: int, dst_granularity: int):
        self._src_granularity = src_granularity
        self._dst_granularity = dst_granularity
        if src_granularity > dst_granularity:
            raise ValueError("src granularity must be less than dst granularity")
        self._ratio = dst_granularity // src_granularity
        self._klines = deque(maxlen=self._ratio)
        self._dst_kline = None
    
    def reset(self):
        self._klines.clear()
        self._dst_kline = None

    def granularity(self):
        """
        Granularity of the klines being emitted
        """
        return self._dst_granularity

    def ready(self):
        return self._dst_kline is not None

    def update(self, kline: Kline):
        """
        Update the kline emitter with a new kline
        """
        if self.ready():
            return
        self._klines.append(kline)
        # if we have enough klines to emit, do so
        if len(self._klines) == self._ratio:
            self._dst_kline = Kline(granularity=self._dst_granularity)

            if kline.symbol:
                self._dst_kline.symbol = kline.symbol

            for i in range(self._ratio):
                k = self._klines[i]
                # set open and close prices
                if i == 0:
                    self._dst_kline.open = k.open
                elif i == self._ratio - 1:
                    self._dst_kline.close = k.close
                    self._dst_kline.ts = k.ts

                # sum up the volume from all klines
                self._dst_kline.volume += k.volume

                # set the high and low prices from all klines
                if k.high > self._dst_kline.high:
                    self._dst_kline.high = k.high
                elif k.low < self._dst_kline.low:
                    self._dst_kline.low = k.low

    def emit(self) -> Kline:
        """
        Emit the kline if it is ready
        """
        if not self.ready():
            return None
        kline = self._dst_kline
        self.reset()

        return kline
