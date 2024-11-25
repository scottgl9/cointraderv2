# base account class for handling account market information

class CryptoAccountBaseMarket(object):
    def get_ticker(self, symbol):
        raise NotImplementedError

    def get_tickers(self):
        raise NotImplementedError

    def get_ticker_symbols(self, currency=None):
        raise NotImplementedError

    def get_min_tickers(self):
        raise NotImplementedError

    def get_max_tickers(self):
        raise NotImplementedError

    def update_ticker(self, symbol, price, ts):
        raise NotImplementedError

    def update_tickers(self, tickers):
        raise NotImplementedError

    def get_klines(self, days=0, hours=1, mode=None, ticker_id=None, granularity=3600):
        raise NotImplementedError

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        raise NotImplementedError
