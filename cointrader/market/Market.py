from .MarketBase import MarketBase
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase

class Market(MarketBase):
    _exchange = None
    def __init__(self, exchange: TraderExchangeBase, logger=None):
        super().__init__(exchange, logger)
        self._exchange = exchange

    def market_ticker_price_get(self, ticker: str) -> float:
        """Get ticker price"""
        return self._exchange.market_ticker_price_get(ticker)

    def market_ticker_prices_all_get(self) -> dict:
        """Get all ticker prices"""
        return self._exchange.market_ticker_prices_all_get()

    def market_get_kline_granularities(self) -> list[int]:
        """Get kline granularities"""
        return self._exchange.market_get_kline_granularities()

    def market_get_max_kline_count(self, granularity: int) -> int:
        """Get max kline count for a given interval"""
        return self._exchange.market_get_max_kline_count(granularity)

    def market_get_klines_range(self, ticker: str, start_ts: int, end_ts: int, granularity: int) -> dict:
        """Get klines for a given range"""
        return self._exchange.market_get_klines_range(ticker, start_ts, end_ts, granularity)

