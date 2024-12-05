# This file contains the Indicator class, which is the base class for all indicators.
from .Kline import Kline

class Indicator:
    _name = None
    _ready = False
    _last_value = None
    _last_kline = None
    def __init__(self, name, **kwargs):
        self._name = name

    def ready(self) -> bool:
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def update(self, kline : Kline) -> dict:
        raise NotImplementedError
    
    def update_with_value(self, value) -> dict:
        raise NotImplementedError

    def increasing(self) -> bool:
        raise NotImplementedError
    
    def decreasing(self) -> bool:
        raise NotImplementedError

    def get_last_value(self) -> tuple:
        raise NotImplementedError
   
    def get_last_kline(self) -> Kline:
        raise NotImplementedError

    def __greater_than__(self, other) -> bool:
        if isinstance(other, Indicator):
            this_value = self.get_last_value()
            other_value = other.get_last_value()
            if isinstance(this_value, tuple) or isinstance(other_value, tuple):
                raise ValueError("this_value tuple size is greater than 1")

            return this_value > other_value
        else:
            return self.get_last_value() > other

    def __less_than__(self, other) -> bool:
        if isinstance(other, Indicator):
            this_value = self.get_last_value()
            other_value = other.get_last_value()
            if isinstance(this_value, tuple) or isinstance(other_value, tuple):
                raise ValueError("this_value tuple size is greater than 1")

            return this_value < other_value
        else:
            return self.get_last_value() < other

    def __eq__(self, other) -> bool:
        if isinstance(other, Indicator):
            return self.get_last_value() == other.get_last_value()
        else:
            return self.get_last_value() == other
