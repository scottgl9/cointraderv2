from .Kline import Kline

class ROC(Indicator):
    def __init__(self, name, period, **kwargs):
        super().__init__(name, **kwargs)
        self.period = period
        self.prices = []  # Store historical prices
        self._last_value = None
        self._ready = False

    def ready(self) -> bool:
        return self._ready

    def reset(self):
        self.prices = []
        self._last_value = None
        self._ready = False

    def update(self, kline: Kline) -> dict:
        # Assuming Kline has a 'close' attribute representing the closing price
        price = kline.close
        self.prices.append(price)

        if len(self.prices) > self.period:
            # Maintain a fixed-size list of prices
            self.prices.pop(0)
            self._ready = True
        else:
            self._ready = False

        if self._ready:
            old_price = self.prices[0]
            if old_price != 0:
                self._last_value = ((price - old_price) / old_price) * 100
            else:
                self._last_value = None
        else:
            self._last_value = None

        self._last_kline = kline
        return {"roc": self._last_value}

    def update_with_value(self, value) -> dict:
        raise NotImplementedError("ROC indicator requires Kline updates.")

    def increasing(self) -> bool:
        return self._last_value is not None and self._last_value > 0

    def decreasing(self) -> bool:
        return self._last_value is not None and self._last_value < 0

    def get_last_value(self) -> tuple:
        return (self._last_value,) if self._last_value is not None else (None,)

    def get_last_kline(self) -> Kline:
        return self._last_kline