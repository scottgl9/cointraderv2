from cointrader.client.TraderClientBase import TraderClientBase
from coinbase.rest import RESTClient
from cointrader.common.SymbolInfo import SymbolInfo
from cointrader.order.OrderResult import OrderResult

class CBADVTraderClient(TraderClientBase):
    MAX_CANDLES = 350
    LIMIT = 250
    def __init__(self, api_key, api_secret, logger=None):
        self._name = "cbadv"
        self.client = RESTClient(api_key=api_key, api_secret=api_secret)
        self.logger = logger
        self._quote_currency_list = ['BTC', 'ETH', 'USDC', 'USD', 'USDT']
        self._excluded_currency_list = ['EUR', 'GBP', 'CDE', 'INTX']
        self._stable_currency_list = ['USD', 'USDC', 'USDT']
        self._equivalent_currency_list = self._stable_currency_list
        self._primary_stable_currency = 'USD'
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

    def _info_get_products(self):
        products = []
        result = self.client.get_products(get_all_products=True).products
        for product in result:
            excluded = False
            for exclude in self._excluded_currency_list:
                if product.product_id.endswith(f"-{exclude}"):
                    excluded = True
                    break
            if excluded:
                continue
            products.append(product)
        return products

    def _info_get_accounts(self):
        accounts = self.client.get_accounts(limit=self.LIMIT).accounts
        for account in accounts:
            print(account.currency)
        return accounts

    def info_get_stable_currencies(self) -> list[str]:
        return self._stable_currency_list
    
    def info_primary_stable_currency(self) -> str:
        """Return primary stable currency"""
        return self._primary_stable_currency

    def info_equivalent_stable_currencies(self) -> list[str]:
        """Return equivalent stable currency"""
        return self._equivalent_currency_list

    def info_base_currencies_list(self) -> list[str]:
        """Return list of all base currency names"""
        result = []
        products = self._info_get_products()
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
        products = self._info_get_products()
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

    def info_ticker_query(self, ticker: str) -> SymbolInfo:
        """Query ticker information"""
        response = self.client.get_product(product_id=ticker)
        result = self.info_ticker_parse(ticker, response)

        return result
    
    def info_ticker_parse(self, ticker: str, response) -> SymbolInfo:
        """Parse ticker information"""
        result = SymbolInfo()
        result.base_name = response.base_currency_id
        result.quote_name = response.quote_currency_id
        result.price = float(response.price)
        result.base_min_size = float(response.base_min_size)
        result.base_step_size = float(response.base_increment)
        result.quote_min_size = float(response.quote_min_size)
        result.quote_step_size = float(response.quote_increment)

        def get_precision(step_size: float) -> int:
            """Get precision based on step size"""
            step_size_str = f"{step_size:.10f}".rstrip('0')
            if '.' in step_size_str:
                return len(step_size_str.split('.')[1])
            return 0

        result.base_precision = get_precision(result.base_step_size)
        result.quote_precision = get_precision(result.quote_step_size)
        #result.base_precision = len(str(result.base_step_size).split('.')[1])
        #result.quote_precision = len(str(result.quote_step_size).split('.')[1])

        return result

    def info_ticker_query_all(self) -> dict[str, SymbolInfo]:
        """Query all tickers"""
        result = {}
        products = self._info_get_products()
        for product in products:
            if self.info_ticker_get_quote(product.product_id) in self._excluded_currency_list:
                continue
            result[product.product_id] = self.info_ticker_parse(product.product_id, product)
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
        products = self._info_get_products()
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
        result = self.client.market_order_buy(product_id=ticker, base_size=amount)
        return self.trade_parse_order_result(result, ticker)
    
    def trade_sell_market(self, ticker: str, amount: float) -> dict:
        """Sell at market price"""
        result = self.client.market_order_sell(client_order_id='', product_id=ticker, base_size=amount)
        return self.trade_parse_order_result(result, ticker)

    def trade_buy_limit(self, ticker: str, amount: float, price: float, type: str) -> dict:
        """Buy at a specific price"""
        result = self.client.limit_order_gtc_buy(client_order_id='', product_id=ticker, limit_price=price, base_size=amount)
        return self.trade_parse_order_result(result, ticker)

    def trade_sell_limit(self, ticker: str, amount: float, price: float, type: str) -> dict:
        """Sell at a specific price"""
        result = self.client.limit_order_gtc_sell(client_order_id='', product_id=ticker, limit_price=price, base_size=amount)
        return self.trade_parse_order_result(result, ticker)

    def trade_buy_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float, type: str) -> dict:
        """Buy at a specific price when stop price is reached"""
        # TODO: implement stop direction
        result = self.client.stop_limit_order_gtc_buy(client_order_id='', product_id=ticker, limit_price=price, stop_price=stop_price, base_size=amount)
        return self.trade_parse_order_result(result, ticker)
    
    def trade_sell_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float, type: str) -> dict:
        """Sell at a specific price when stop price is reached"""
        # TODO: implement stop direction
        return self.client.stop_limit_order_gtc_sell(client_order_id='', product_id=ticker, limit_price=price, stop_price=stop_price, base_size=amount)

    def trade_cancel(self, ticker: str, order_id: str) -> dict:
        """Cancel an open order"""
        result = self.client.cancel_orders(order_ids=[order_id])
        return self.trade_parse_order_result(result, ticker)

    def trade_get_order(self, ticker: str, order_id: str) -> dict:
        """Get order information"""
        result = self.client.get_order(order_id=order_id)
        return self.trade_parse_order_result(result, ticker)

    def trade_get_open_orders(self, ticker: str) -> dict:
        """Get open orders"""
        raise NotImplementedError

    def trade_get_closed_orders(self, ticker: str) -> dict:
        """Get closed orders"""
        raise NotImplementedError
    
    def trade_parse_order_result(self, result, ticker: str) -> OrderResult:
        """Parse trade order result"""
        print(result)
        order_result = OrderResult(symbol=ticker)
        return order_result
