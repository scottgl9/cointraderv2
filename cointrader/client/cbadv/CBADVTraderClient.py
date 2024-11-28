from cointrader.client.TraderClientBase import TraderClientBase
from coinbase.rest import RESTClient
from cointrader.common.AssetInfo import AssetInfo

class CBADVTraderClient(TraderClientBase):
    MAX_CANDLES = 350
    def __init__(self, api_key, api_secret, logger=None):
        self._name = "cbadv"
        self.client = RESTClient(api_key=api_key, api_secret=api_secret)
        self.logger = logger
        self._quote_currency_list = ['BTC', 'ETH', 'USDC', 'USD', 'USDT']
        self._excluded_currency_list = ['EUR', 'GBP']
        self._granularity_mapping = {
            60: 'ONE_MINUTE',
            300: 'FIVE_MINUTE',
            900: 'FIFTEEN_MINUTE',
            3600: 'ONE_HOUR',
            21600: 'SIX_HOUR',
            86400: 'ONE_DAY',
        }

    def get_client(self) -> RESTClient:
        return self.client

    def info_base_currencies_list(self) -> list[str]:
        """Return list of all base currency names"""
        result = []
        products = self.client.get_products().products
        for product in products:
            if product.base_currency_id not in result:
                result.append(product.base_currency_id)
        return result

    # return list of all quote currency names
    def info_quote_currencies_list(self) -> list[str]:
        """Return list of all quote currency names"""
        return self._quote_currency_list

    def info_ticker_names_list(self) -> list[str]:
        """
        Return list of all ticker names
        """
        result = []
        products = self.client.get_products().products
        for product in products:
            #  ignored currencies
            if self.info_ticker_get_quote(product.product_id) in self._excluded_currency_list:
                continue
            result.append(product.product_id)
        return result
   
    def info_ticker_join(self, base: str, quote: str) -> str:
        """Create a ticker from base and quote currency names"""
        return f"{base}-{quote}"

    def info_ticker_split(self, ticker: str) -> tuple[str, str]:
        """Split ticker into base and quote currency names"""
        return tuple(ticker.split('-'))

    def info_ticker_query(self, ticker: str) -> AssetInfo:
        """Query ticker information"""
        response = self.client.get_product(product_id=ticker)
        result = AssetInfo()
        result.base_name = response.base_currency_id
        result.quote_name = response.quote_currency_id
        result.price = float(response.price)
        result.base_min_size = float(response.base_min_size)
        result.base_step_size = float(response.base_increment)
        result.quote_min_size = float(response.quote_min_size)
        result.quote_step_size = float(response.quote_increment)
        result.base_precision = len(str(result.base_step_size).split('.')[1])
        result.quote_precision = len(str(result.quote_step_size).split('.')[1])

        return result

    def info_ticker_query_all(self) -> dict[str, AssetInfo]:
        """Query all tickers"""
        result = {}
        products = self.client.get_products(limit=250).products
        for product in products:
            if self.info_ticker_get_quote(product.product_id) in self._excluded_currency_list:
                continue
            result[product.product_id] = self.info_ticker_query(product.product_id)
        return result

    def info_currency_query(self, currency: str) -> dict:
        """Query currency information"""
        raise NotImplementedError


    def account_get_ids(self) -> dict:
        """Get account ids if account is multi-account"""
        raise NotImplementedError

    def account_get_maker_fee(self) -> float:
        """Get maker trade fee"""
        return self.client.get_transaction_summary().fee_tier['maker_fee_rate']

    def account_get_taker_fee(self) -> float:
        """Get taker trade fee"""
        return self.client.get_transaction_summary().fee_tier['taker_fee_rate']


    def balance_get(self, currency: str) -> tuple[float, float]:
        """Get balance of currency"""
        accounts = self.client.get_accounts(limit=250).accounts
        for account in accounts:
            if account.currency == currency:
                available_balance = float(account.available_balance['value'])
                hold_balance = float(account.hold['value'])
                return (available_balance, hold_balance)

    def balance_set(self, currency: str, available: float, hold: float) -> None:
        """Set balance of currency (used for testing)"""
        pass

    def balance_all_get(self) -> dict[str, tuple[float, float]]:
        """Get all balances"""
        accounts = self.client.get_accounts(limit=250).accounts
        result = {}
        for account in accounts:
            available_balance = float(account.available_balance['value'])
            hold_balance = float(account.hold['value'])
            result[account.currency] = (available_balance, hold_balance)
        return result

    def market_ticker_price_get(self, ticker: str) -> float:
        """Get ticker information"""
        response = self.client.get_product(product_id=ticker)
        return float(response.price)

    def market_ticker_prices_all_get(self) -> dict:
        """Get all ticker prices"""
        result = {}
        products = self.client.get_products(limit=250).products
        for product in products:
            result[product.product_id] = float(product.price)
        return result

    def market_get_orderbook(self, ticker: str, level: int) -> dict: 
        """Get orderbook"""
        raise NotImplementedError
    
    def market_get_trades(self, ticker: str, limit: int) -> dict:
        """Get trades for ticker for a given limit"""
        raise NotImplementedError

    def market_get_kline_granularities(self) -> list[int]:
        """Get kline granularities"""
        return list(self._granularity_mapping.keys())

    def market_get_max_kline_count(self, granularity: int) -> int:
        """Get max kline count for a given interval"""
        return self.MAX_CANDLES

    def market_get_klines_range(self, ticker: str, start_ts: int, end_ts: int, granularity: int) -> dict:
        """Get klines for ticker for a given interval and time range"""
        candles = self.client.get_candles(ticker, start_ts, end_ts, granularity=self._granularity_mapping[granularity])
        candles = candles['candles']
        #candles = [candle.__repr__() for candle in candles]
        candles = [candle.__dict__ for candle in candles]
        return candles

    def trade_buy_market(self, ticker: str, amount: float) -> dict:
        """Buy at market price"""
        return self.client.market_order_buy(product_id=ticker, base_size=amount)
    
    def trade_sell_market(self, ticker: str, amount: float) -> dict:
        """Sell at market price"""
        return self.client.market_order_sell(client_order_id='', product_id=ticker, base_size=amount)

    def trade_buy_limit(self, ticker: str, amount: float, price: float, type: str) -> dict:
        """Buy at a specific price"""
        return self.client.limit_order_gtc_buy(client_order_id='', product_id=ticker, limit_price=price, base_size=amount)
    
    def trade_sell_limit(self, ticker: str, amount: float, price: float, type: str) -> dict:
        """Sell at a specific price"""
        return self.client.limit_order_gtc_sell(client_order_id='', product_id=ticker, limit_price=price, base_size=amount)

    def trade_buy_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float, type: str) -> dict:
        """Buy at a specific price when stop price is reached"""
        # TODO: implement stop direction
        return self.client.stop_limit_order_gtc_buy(client_order_id='', product_id=ticker, limit_price=price, stop_price=stop_price, base_size=amount)
    
    def trade_sell_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float, type: str) -> dict:
        """Sell at a specific price when stop price is reached"""
        # TODO: implement stop direction
        return self.client.stop_limit_order_gtc_sell(client_order_id='', product_id=ticker, limit_price=price, stop_price=stop_price, base_size=amount)

    def trade_cancel(self, ticker: str, order_id: str) -> dict:
        """Cancel an open order"""
        return self.client.cancel_orders(order_ids=[order_id])
    
    def trade_get_order(self, ticker: str, order_id: str) -> dict:
        """Get order information"""
        return self.client.get_order(order_id=order_id)

    def trade_get_open_orders(self, ticker: str) -> dict:
        """Get open orders"""
        raise NotImplementedError

    def trade_get_closed_orders(self, ticker: str) -> dict:
        """Get closed orders"""
        raise NotImplementedError
    
    def trade_parse_order_result(self, result: str, ticker: str, sigid: int) -> dict:
        """Parse trade order result"""
        raise NotImplementedError

