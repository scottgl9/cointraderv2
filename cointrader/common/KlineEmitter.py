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
        print(f"src_gran: {src_granularity} dst_gran: {dst_granularity} ratio: {self._ratio}")
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
        self._klines.append(kline)
        # if we have enough klines to emit, do so
        if len(self._klines) == self._ratio:
            self._dst_kline = Kline(granularity=self._dst_granularity)

            if kline.symbol:
                self._dst_kline.symbol = kline.symbol

            # set open and close prices
            self._dst_kline.open = self._klines[0].open
            self._dst_kline.close = self._klines[-1].close
            self._dst_kline.ts = self._klines[-1].ts
            self._dst_kline.volume = 0
            self._dst_kline.high = self._klines[0].high
            self._dst_kline.low = self._klines[0].low

            for i in range(self._ratio):
                k = self._klines[i]
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

        return kline
