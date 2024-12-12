# Kline (OHLCV) class

class Kline(object):
    symbol = None
    open = 0
    close = 0
    low = 0
    high = 0
    volume = 0
    ts = 0
    granularity = None
    # name of the symbol field in the dict
    symbol_name = 'symbol'
    open_name = 'open'
    close_name = 'close'
    low_name = 'low'
    high_name = 'high'
    volume_name = 'volume'
    ts_name = 'ts'

    def __init__(self, symbol=None, open=0, close=0, low=0, high=0,
                 volume=0, ts=0, granularity=None):
        self.symbol = symbol
        self.open = open
        self.close = close
        self.low = low
        self.high = high
        self.volume = volume
        self.ts = ts
        self.granularity = granularity

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
    
    def __eq__(self, other):
        return self.__dict__() == other.__dict__()

    def reset(self):
        """
        Resets the Kline object
        """
        self.symbol = None
        self.open = 0
        self.close = 0
        self.low = 0
        self.high = 0
        self.volume = 0
        self.ts = 0

    def copy(self):
        """
        Returns a copy of the Kline object
        """
        kline = Kline()
        kline.symbol_name = self.symbol_name
        kline.open_name = self.open_name
        kline.close_name = self.close_name
        kline.low_name = self.low_name
        kline.high_name = self.high_name
        kline.volume_name = self.volume_name
        kline.ts_name = self.ts_name

        kline.symbol = self.symbol
        kline.open = self.open
        kline.close = self.close
        kline.low = self.low
        kline.high = self.high
        kline.volume = self.volume
        kline.ts = self.ts

        return kline