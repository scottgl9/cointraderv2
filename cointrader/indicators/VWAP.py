from .Kline import Kline

class VWAP(Indicator):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.cumulative_volume = 0.0
        self.cumulative_price_volume = 0.0
        self._last_value = None
        self._ready = False

    def ready(self) -> bool:
        return self._ready

    def reset(self):
        self.cumulative_volume = 0.0
        self.cumulative_price_volume = 0.0
        self._last_value = None
        self._ready = False

    def update(self, kline: Kline) -> dict:
        # Assuming Kline has 'close', 'high', 'low', and 'volume' attributes
        typical_price = (kline.close + kline.high + kline.low) / 3
        volume = kline.volume

        # Update cumulative values
        self.cumulative_price_volume += typical_price * volume
        self.cumulative_volume += volume

        if self.cumulative_volume > 0:
            self._last_value = self.cumulative_price_volume / self.cumulative_volume
            self._ready = True
        else:
            self._last_value = None
            self._ready = False

        self._last_kline = kline
        return {"vwap": self._last_value}

    def update_with_value(self, value) -> dict:
        raise NotImplementedError("VWAP indicator requires Kline updates.")

    def increasing(self) -> bool:
        return self._last_value is not None and self._last_value > (self._last_kline.close if self._last_kline else 0)

    def decreasing(self) -> bool:
        return self._last_value is not None and self._last_value < (self._last_kline.close if self._last_kline else 0)

    def get_last_value(self) -> tuple:
        return (self._last_value,) if self._last_value is not None else (None,)

    def get_last_kline(self) -> Kline:
        return self._last_kline