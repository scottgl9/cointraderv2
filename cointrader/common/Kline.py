# Kline (OHLCV) class

class Kline(object):
    symbol = None
    open = 0
    close = 0
    low = 0
    high = 0
    volume = 0
    ts = 0
    # name of the symbol field in the dict
    symbol_name = None
    open_name = 'open'
    close_name = 'close'
    low_name = 'low'
    high_name = 'high'
    volume_name = 'volume'
    ts_name = 'ts'

    def __init__(self, symbol=None, open=0, close=0, low=0, high=0,
                 volume=0, ts=0):
        self.symbol = symbol
        self.open = open
        self.close = close
        self.low = low
        self.high = high
        self.volume = volume
        self.ts = ts

    def set_dict_names(self, symbol=None, open='open', close='close', 
                       low='low', high='high', volume='volume', ts='ts'):
        self.symbol_name = symbol
        self.open_name = open
        self.close_name = close
        self.low_name = low
        self.high_name = high
        self.volume_name = volume
        self.ts_name = ts

    def from_dict(self, data):
        if self.symbol_name:
            self.symbol = data.get(self.symbol_name)
        self.open = float(data.get(self.open_name))
        self.close = float(data.get(self.close_name))
        self.low = float(data.get(self.low_name))
        self.high = float(data.get(self.high_name))
        self.volume = float(data.get(self.volume_name))
        self.ts = int(data.get(self.ts_name))

    def __dict__(self):
        return {
            self.symbol_name: self.symbol,
            self.open_name: float(self.open),
            self.close_name: float(self.close),
            self.low_name: float(self.low),
            self.high_name: float(self.high),
            self.volume_name: float(self.volume),
            self.ts_name: int(self.ts)
        }

    def __repr__(self):
        return self.__dict__()

    def __str__(self):
        return str(self.__repr__())

    def reset(self):
        self.symbol = None
        self.open = 0
        self.close = 0
        self.low = 0
        self.high = 0
        self.volume = 0
        self.ts = 0
