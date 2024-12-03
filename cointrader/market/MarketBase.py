from cointrader.exchange.TraderExchangeBase import TraderExchangeBase

class MarketBase(object):
    _exchange = None
    _logger = None
    def __init__(self, exchange: TraderExchangeBase, logger=None):
        self._cline = exchange
        self._logger = logger
    
    def exchange(self):
        return self._exchange

    def market_ticker_price_get(self, ticker: str) -> float:
        """Get ticker price"""
        raise NotImplementedError

    def market_ticker_prices_all_get(self) -> dict:
        """Get all ticker prices"""
        raise NotImplementedError

    def market_get_kline_granularities(self) -> list[int]:
        """Get kline granularities"""
        raise NotImplementedError

    def market_get_max_kline_count(self, granularity: int) -> int:
        """Get max kline count for a given interval"""
        raise NotImplementedError

    def market_get_klines_range(self, ticker: str, start_ts: int, end_ts: int, granularity: int) -> dict:
        """Get klines for a given range"""
        raise NotImplementedError
