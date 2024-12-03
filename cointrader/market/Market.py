from .MarketBase import MarketBase
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from .MarketStorage import MarketStorage

class Market(MarketBase):
    _exchange = None
    def __init__(self, exchange: TraderExchangeBase, db_path='market_data.db', logger=None):
        super().__init__(exchange, logger)
        self._exchange = exchange
        self._db_path = db_path
        self._storage = MarketStorage(db_path)

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

    def market_get_klines_range(self, ticker: str, start_ts: int, end_ts: int, granularity: int, store_db=False) -> dict:
        """Get klines for a given range"""
        if store_db:
            max_klines = self._exchange.market_get_max_kline_count(granularity)
            # if the table exists, get klines from the database
            if self._storage.table_exists(ticker, granularity):
                klines = self._storage.get_klines_range(ticker, start_ts, end_ts, granularity)
                for kline in klines:
                    if not self._storage.kline_exists(symbol=ticker, ts=kline['ts'], granularity=granularity):
                        break
                    start_ts += granularity * max_klines

                # if all kliness are in the database, return them
                if start_ts >= end_ts:
                    return klines
                
                # get klines from the exchange and store them in the database
                new_klines = self._exchange.market_get_klines_range(ticker, start_ts, end_ts, granularity)
                for kline in new_klines:
                    self._storage.store_kline(ticker, open=kline['open'], high=kline['high'], low=kline['low'], close=kline['close'], volume=kline['volume'], ts=kline['start'], granularity=granularity)
                    klines.append(kline)
                return klines
            else:
                self._storage.create_table(ticker, granularity)
                # get klines from the exchange and store them in the database
                klines = self._exchange.market_get_klines_range(ticker, start_ts, end_ts, granularity)
                for kline in klines:
                    self._storage.store_kline(ticker, open=kline['open'], high=kline['high'], low=kline['low'], close=kline['close'], volume=kline['volume'], ts=kline['start'], granularity=granularity)
                return klines
        else:
            return self._exchange.market_get_klines_range(ticker, start_ts, end_ts, granularity)
