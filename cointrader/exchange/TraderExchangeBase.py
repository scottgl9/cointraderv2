# TraderExchangeBase is the base class for all exchange specific implementations
from cointrader.common.SymbolInfo import SymbolInfo
from cointrader.order.OrderResult import OrderResult
from cointrader.order.enum.OrderStopDirection import OrderStopDirection

class TraderExchangeBase(object):
    _name = None
    def __init__(self):
        self._name = "base"


    def name(self) -> str:
        """Return name of exchange"""
        return self._name

    def get_client(self):
        """Return exchange client"""
        raise NotImplementedError

    def reconnect(self):
        """Reconnect to exchange"""
        raise NotImplementedError

    def info_get_stable_currencies(self) -> list[str]:
        """Return list of stable currencies"""
        raise NotImplementedError
    
    def info_equivalent_stable_currencies(self) -> list[str]:
        """Return equivalent stable currencies"""
        raise NotImplementedError
    
    def info_primary_stable_currency(self) -> str:
        """Return primary stable currency"""
        raise NotImplementedError

    # return list of all base currency names
    def info_base_currencies_list(self) -> list[str]:
        """Return list of all base currency names"""
        raise NotImplementedError
    
    # return list of all quote currency names
    def info_quote_currencies_list(self) -> list[str]:
        """Return list of all quote currency names"""
        raise NotImplementedError
    
    def info_ticker_names_list(self) -> list[str]:
        """
        Return list of all ticker names
        tickers are the combined base and quote names
        For example, for Coinbase Advanced, 'BTC-USD' is a ticker
        """
        raise NotImplementedError
   
    def info_ticker_join(self, base: str, quote: str) -> str:
        """Create a ticker from base and quote currency names"""
        raise NotImplementedError

    def info_ticker_split(self, ticker: str) -> tuple[str, str]:
        """Split ticker into base and quote currency names"""
        raise NotImplementedError

    def info_ticker_get_base(self, ticker: str) -> str:
        """Get base currency name from ticker"""
        return self.info_ticker_split(ticker)[0]
    
    def info_ticker_get_quote(self, ticker: str) -> str:
        """Get quote currency name from ticker"""
        return self.info_ticker_split(ticker)[1]

    def info_ticker_query(self, ticker: str) -> SymbolInfo:
        """Query ticker information"""
        raise NotImplementedError

    def info_ticker_parse(self, ticker: str, response) -> SymbolInfo:
        """Parse ticker information"""
        raise NotImplementedError

    def info_ticker_query_all(self) -> dict[str, SymbolInfo]:
        """Query all tickers for information"""
        raise NotImplementedError

    def info_currency_query(self, currency: str) -> dict:
        """Query currency information"""
        raise NotImplementedError


    def account_get_ids(self) -> dict:
        """Get account ids if account is multi-account"""
        raise NotImplementedError

    def account_get_maker_fee(self) -> float:
        """Get maker trade fee"""
        raise NotImplementedError

    def account_get_taker_fee(self) -> float:
        """Get taker trade fee"""
        raise NotImplementedError


    def balance_get(self, currency: str) -> float:
        """Get balance of currency"""
        raise NotImplementedError

    def balance_set(self, currency: str, value: float) -> None:
        """Set balance of currency (used for testing)"""
        raise NotImplementedError

    def balance_get(self, currency: str) -> tuple[float, float]:
        """Get balance of currency"""
        raise NotImplementedError

    def balance_set(self, currency: str, available: float, hold: float) -> None:
        """Set balance of currency (used for testing)"""
        raise NotImplementedError

    def balance_all_get(self) -> dict[str, tuple[float, float]]:
        """Get all balances with non-zero values"""
        raise NotImplementedError


    def market_ticker_price_get(self, ticker: str) -> dict:
        """Get ticker information"""
        raise NotImplementedError
    
    def market_ticker_prices_all_get(self) -> dict:
        """Get all tickers"""
        raise NotImplementedError

    def market_get_orderbook(self, ticker: str, level: int) -> dict: 
        """Get orderbook"""
        raise NotImplementedError
    
    def market_get_trades(self, ticker: str, limit: int) -> dict:
        """Get trades for ticker for a given limit"""
        raise NotImplementedError

    def market_get_kline_granularities(self) -> list[int]:
        """Get kline granularities"""
        raise NotImplementedError

    def market_get_max_kline_count(self, granularity: int) -> int:
        """Get max kline count for a given interval"""
        raise NotImplementedError

    def market_get_klines_range(self, ticker: str, start_ts: int, end_ts: int, granularity: int) -> list:
        """Get klines for a given range"""
        raise NotImplementedError


    def trade_buy_market(self, ticker: str, amount: float) -> dict:
        """Buy at market price"""
        raise NotImplementedError
    
    def trade_sell_market(self, ticker: str, amount: float) -> dict:
        """Sell at market price"""
        raise NotImplementedError

    def trade_buy_limit(self, ticker: str, amount: float, price: float, type: str) -> dict:
        """Buy at a specific price"""
        raise NotImplementedError
    
    def trade_sell_limit(self, ticker: str, amount: float, price: float, type: str) -> dict:
        """Sell at a specific price"""
        raise NotImplementedError
    
    def trade_buy_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float, stop_direction: OrderStopDirection, type: str = "") -> dict:
        """Buy at a specific price when stop price is reached"""
        raise NotImplementedError
    
    def trade_sell_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float, stop_direction: OrderStopDirection, type: str = "") -> dict:
        """Sell at a specific price when stop price is reached"""
        raise NotImplementedError

    def trade_cancel_order(self, ticker: str, order_id: str) -> dict:
        """Cancel an open order"""
        raise NotImplementedError
    
    def trade_get_order(self, ticker: str, order_id: str) -> dict:
        """Get order information"""
        raise NotImplementedError
   
    def trade_get_open_orders(self, ticker: str) -> dict:
        """Get open orders"""
        raise NotImplementedError
    
    def trade_get_closed_orders(self, ticker: str) -> dict:
        """Get closed orders"""
        raise NotImplementedError
    
    def trade_parse_order_result(self, result, ticker: str) -> OrderResult:
        """Parse trade order result"""
        raise NotImplementedError
