# This file contains the Strategy class which is the base class for all strategies
from .Kline import Kline

class Strategy:
    _name = None
    _symbol = None
    _kwargs = None

    def __init__(self, symbol, name, **kwargs):
        self._name = name
        self._symbol = symbol
        self._kwargs = kwargs

    def update(self, kline : Kline):
        raise NotImplementedError
    
    def buy_signal_name(self):
        raise NotImplementedError

    def sell_signal_name(self):
        raise NotImplementedError

    def buy_signal(self):
        raise NotImplementedError
    
    def sell_signal(self):
        raise NotImplementedError
