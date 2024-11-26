# This file contains the Indicator class, which is the base class for all indicators.
from .Kline import Kline

class Indicator:
    name = None
    def __init__(self, name, **kwargs):
        self.name = name

    def update(self, kline : Kline):
        raise NotImplementedError
    
    def get_last_value(self):
        raise NotImplementedError
    
    def get_last_timestamp(self):
        raise NotImplementedError

    def get_last_kline(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def __greater_than__(self, other):
        raise NotImplementedError
    
    def __less_than__(self, other):
        raise NotImplementedError

