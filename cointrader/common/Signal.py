# This file contains the Signal class which is the base class for all signals
from .Kline import Kline

class Signal:
    name = None
    symbol = None
    def __init__(self, name, symbol, **kwargs):
        self.name = name
        self.symbol = symbol

    def update(self, kline : Kline):
        raise NotImplementedError
    
    def buy_signal(self):
        raise NotImplementedError
    
    def sell_signal(self):
        raise NotImplementedError
