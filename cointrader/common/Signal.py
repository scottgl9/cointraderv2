# This file contains the Signal class which is the base class for all signals
from .Kline import Kline

class Signal:
    _name = None
    _symbol = None
    _values = None
    _cross_up = False
    _cross_down = False

    def __init__(self, name, symbol, **kwargs):
        self._name = name
        self._symbol = symbol

    def ready(self):
        raise NotImplementedError
    
    def reset(self):
        raise NotImplementedError

    def update(self, kline : Kline):
        raise NotImplementedError
    
    def cross_up(self):
        raise NotImplementedError
    
    def cross_down(self):
        raise NotImplementedError
    
    def above(self):
        raise NotImplementedError
    
    def below(self):
        raise NotImplementedError

    def buy_signal(self):
        raise NotImplementedError
    
    def sell_signal(self):
        raise NotImplementedError
