from .Kline import Kline

class Strategy:
    name = None
    symbol = None

    def __init__(self, name, symbol, **kwargs):
        self.name = name
        self.symbol = symbol
        self.kwargs = kwargs

    def update(self, kline : Kline):
        raise NotImplementedError
    
    def buy(self):
        raise NotImplementedError
    
    def sell(self):
        raise NotImplementedError
