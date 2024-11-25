# TraderClientBase is the base class for all exchange specific implementations

class TraderClientBase(object):
    def __init__(self) -> None:
        pass

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
   
    def info_ticker_create(self, base: str, quote: str) -> str:
        """Create a ticker from base and quote currency names"""
        raise NotImplementedError
    
    def info_ticker_split(self, ticker: str) -> tuple[str, str]:
        """Split ticker into base and quote currency names"""
        raise NotImplementedError

    def info_ticker_get_base(self, ticker: str) -> str:
        """Get base currency name from ticker"""
        raise NotImplementedError
    
    def info_ticker_get_quote(self, ticker: str) -> str:
        """Get quote currency name from ticker"""
        raise NotImplementedError

    def info_ticker_query(self, ticker: str) -> dict:
        """Query ticker information"""
        raise NotImplementedError
    
    def info_currency_query(self, currency: str) -> dict:
        """Query currency information"""
        raise NotImplementedError


    def account_get_ids(self) -> dict:
        """Get account ids if account is multi-account"""
        raise NotImplementedError

    def account_get_market_fee(self) -> float:
        """Get market trade fee"""
        raise NotImplementedError

    def account_get_limit_fee(self) -> float:
        """Get limit trade fee"""
        raise NotImplementedError


    def balance_get(self, currency: str) -> float:
        """Get balance of currency"""
        raise NotImplementedError

    def balance_set(self, currency: str, value: float) -> None:
        """Set balance of currency (used for testing)"""
        raise NotImplementedError

    def balance_get_all(self) -> dict[str, float]:
        """Get all balances with non-zero values"""
        raise NotImplementedError


    def market_get_ticker(self, ticker: str) -> dict:
        """Get ticker information"""
        raise NotImplementedError
    
    def market_get_tickers(self) -> dict:
        """Get all tickers"""
        raise NotImplementedError

    def market_get_orderbook(self, ticker: str, level: int) -> dict: 
        """Get orderbook"""
        raise NotImplementedError
    
    def market_get_trades(self, ticker: str, limit: int) -> dict:
        """Get trades for ticker for a given limit"""
        raise NotImplementedError
    
    def market_get_klines(self, ticker: str, interval: str, limit: int) -> dict:
        """Get klines for ticker for a given interval and limit"""
        raise NotImplementedError
    
    def market_get_klines_range(self, ticker: str, interval: str, start_ts: int, end_ts: int) -> dict:
        """Get klines for ticker for a given interval and time range"""
        raise NotImplementedError


    def trade_buy_market(self, ticker: str, amount: float) -> dict:
        """Buy at market price"""
        raise NotImplementedError
    
    def trade_sell_market(self, ticker: str, amount: float) -> dict:
        """Sell at market price"""
        raise NotImplementedError
    
    def trade_buy_limit(self, ticker: str, amount: float, price: float) -> dict:
        """Buy at a specific price"""
        raise NotImplementedError
    
    def trade_sell_limit(self, ticker: str, amount: float, price: float) -> dict:
        """Sell at a specific price"""
        raise NotImplementedError
    
    def trade_buy_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float) -> dict:
        """Buy at a specific price when stop price is reached"""
        raise NotImplementedError
    
    def trade_sell_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float) -> dict:
        """Sell at a specific price when stop price is reached"""
        raise NotImplementedError

    def trade_cancel(self, ticker: str, order_id: str) -> dict:
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
    
    def trade_parse_order_result(self, result: str, ticker: str, sigid: int) -> dict:
        """Parse trade order result"""
        raise NotImplementedError
    
