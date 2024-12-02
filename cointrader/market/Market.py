from .MarketBase import MarketBase
from cointrader.client.TraderClientBase import TraderClientBase

class Market(MarketBase):
    _client = None
    def __init__(self, client: TraderClientBase, logger=None):
        super().__init__(client, logger)
        self._client = client

    def market_ticker_price_get(self, ticker: str) -> float:
        """Get ticker price"""
        return self._client.market_ticker_price_get(ticker)

    def market_ticker_prices_all_get(self) -> dict:
        """Get all ticker prices"""
        return self._client.market_ticker_prices_all_get()

    def market_get_kline_granularities(self) -> list[int]:
        """Get kline granularities"""
        return self._client.market_get_kline_granularities()

    def market_get_max_kline_count(self, granularity: int) -> int:
        """Get max kline count for a given interval"""
        return self._client.market_get_max_kline_count(granularity)

    def market_get_klines_range(self, ticker: str, start_ts: int, end_ts: int, granularity: int) -> dict:
        """Get klines for a given range"""
        return self._client.market_get_klines_range(ticker, start_ts, end_ts, granularity)

