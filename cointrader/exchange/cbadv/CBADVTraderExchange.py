from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from coinbase.rest import RESTClient
from coinbase.rest.types.orders_types import GetOrderResponse
from cointrader.common.SymbolInfo import SymbolInfo
from cointrader.order.OrderResult import OrderResult
from cointrader.order.OrderStatus import OrderStatus
from cointrader.order.OrderSide import OrderSide
from cointrader.order.OrderType import OrderType
from cointrader.order.OrderLimitType import OrderLimitType
from cointrader.order.OrderStopDirection import OrderStopDirection
from cointrader.order.OrderErrorReason import OrderErrorReason
from datetime import datetime

class CBADVTraderExchange(TraderExchangeBase):
    MAX_CANDLES = 350
    LIMIT = 250
    STOP_DIRECTION_DOWN = "STOP_DIRECTION_STOP_DOWN"
    STOP_DIRECTION_UP = "STOP_DIRECTION_STOP_UP"
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
        try:
            result = float(response.price)
        except ValueError:
            result = 0.0
        return result

    def market_ticker_prices_all_get(self) -> dict:
        """Get all ticker prices"""
        result = {}
        products = self._info_get_products()
        for product in products:
            try:
                result[product.product_id] = float(product.price)
            except ValueError:
                result[product.product_id] = 0.0
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

    def market_get_klines_range(self, ticker: str, start_ts: int, end_ts: int, granularity: int) -> list:
        """Get klines for ticker for a given interval and time range"""
        candles = self.client.get_candles(ticker, start_ts, end_ts, granularity=self._granularity_mapping[granularity])
        candles = candles['candles']
        #candles = [candle.__repr__() for candle in candles]
        candles = [candle.__dict__ for candle in candles]
        return candles

    def trade_buy_market(self, ticker: str, amount: float) -> dict:
        """Buy at market price"""
        try:
            result = self.client.market_order_buy(client_order_id='', product_id=ticker, base_size=str(amount))
        except Exception as e:
            result = {}
            result['success'] = False
            result['response'] = { 'error': 'UNKNOWN', 'message': str(e) }
        return self.trade_parse_order_result(result, ticker)
    
    def trade_sell_market(self, ticker: str, amount: float) -> dict:
        """Sell at market price"""
        try:
            result = self.client.market_order_sell(client_order_id='', product_id=ticker, base_size=str(amount))
        except Exception as e:
            result = {}
            result['success'] = False
            result['response'] = { 'error': 'UNKNOWN', 'message': str(e) }

        return self.trade_parse_order_result(result, ticker)

    def trade_buy_limit(self, ticker: str, amount: float, price: float, type: str = "") -> dict:
        """Buy at a specific price"""
        try:
            result = self.client.limit_order_gtc_buy(client_order_id='', product_id=ticker, limit_price=str(price), base_size=str(amount))
        except Exception as e:
            result = {}
            result['success'] = False
            result['response'] = { 'error': 'UNKNOWN', 'message': str(e) }
        return self.trade_parse_order_result(result, ticker)

    def trade_sell_limit(self, ticker: str, amount: float, price: float, type: str = "") -> dict:
        """Sell at a specific price"""
        try:
            result = self.client.limit_order_gtc_sell(client_order_id='', product_id=ticker, limit_price=str(price), base_size=str(amount))
        except Exception as e:
            result = {}
            result['success'] = False
            result['response'] = { 'error': 'UNKNOWN', 'message': str(e) }
        return self.trade_parse_order_result(result, ticker)

    def trade_buy_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float, stop_direction: OrderStopDirection = OrderStopDirection.ABOVE, type: str = "") -> dict:
        """Buy at a specific price when stop price is reached"""
        if stop_direction == OrderStopDirection.BELOW:
            direction = self.STOP_DIRECTION_DOWN
        else:
            direction = self.STOP_DIRECTION_UP
        try:
            result = self.client.stop_limit_order_gtc_buy(client_order_id='',
                                                          product_id=ticker,
                                                          limit_price=str(price),
                                                          stop_price=str(stop_price),
                                                          stop_direction=direction,
                                                          base_size=str(amount))
        except Exception as e:
            result = {}
            result['success'] = False
            result['response'] = { 'error': 'UNKNOWN', 'message': str(e) }
        return self.trade_parse_order_result(result, ticker)

    def trade_sell_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float, stop_direction: OrderStopDirection = OrderStopDirection.BELOW, type: str = "") -> dict:
        """Sell at a specific price when stop price is reached"""
        if stop_direction == OrderStopDirection.ABOVE:
            direction = self.STOP_DIRECTION_UP
        else:
            direction = self.STOP_DIRECTION_DOWN
        try:
            result = self.client.stop_limit_order_gtc_sell(client_order_id='',
                                                           product_id=ticker,
                                                           limit_price=str(price),
                                                           stop_price=str(stop_price),
                                                           stop_direction=direction,
                                                           base_size=str(amount))
        except Exception as e:
            result = {}
            result['success'] = False
            result['response'] = { 'error': 'UNKNOWN', 'message': str(e) }
        return self.trade_parse_order_result(result, ticker)

    def trade_cancel_order(self, ticker: str, order_id: str) -> dict:
        """Cancel an open order"""
        try:
            result = self.client.cancel_orders(order_ids=[order_id])
        except Exception as e:
            result = {}
            result['success'] = False
            result['response'] = { 'error': 'UNKNOWN', 'message': str(e) }
        return self.trade_parse_order_result(result, ticker)

    def trade_get_order(self, ticker: str, order_id: str) -> dict:
        """Get order information"""
        try:
            result = self.client.get_order(order_id=order_id)
        except Exception as e:
            result = {}
            result['success'] = False
            result['response'] = { 'error': 'UNKNOWN', 'message': str(e) }
        return self.trade_parse_order_result(result, ticker)

    def trade_get_open_orders(self, ticker: str) -> dict:
        """Get open orders"""
        raise NotImplementedError

    def trade_get_closed_orders(self, ticker: str) -> dict:
        """Get closed orders"""
        raise NotImplementedError

    def trade_parse_order_result(self, result: GetOrderResponse, ticker: str) -> OrderResult:
        """Parse trade order result"""
        order_result = OrderResult(symbol=ticker)
        sub_result = None

        if isinstance(result, dict):
            if 'success' in result:
                if not result['success']:
                    response = result['response']
                    if 'error' in response:
                        if response['error'] == "UNKNOWN":
                            order_result.error_reason = OrderErrorReason.UNKNOWN
                            order_result.error_msg = response['message']
                            return order_result
                        elif response['error'] == "INSUFFICIENT_FUND":
                            order_result.error_reason = OrderErrorReason.INSUFFIENT_BALANCE
                            order_result.error_msg = response['message']
                            return order_result

        print(result)
        if 'response' in result:
            if not result['success']:
                response = result['response']
                order_result.status = OrderStatus.REJECTED
                if response['error'] == "UNKNOWN":
                    order_result.error_reason = OrderErrorReason.UNKNOWN
                elif response['error'] == "INSUFFICIENT_FUND":
                    order_result.error_reason = OrderErrorReason.INSUFFIENT_BALANCE
                else:
                    order_result.error_reason = OrderErrorReason.UNKNOWN
                    print("Unknown error: ", response['error'])
                order_result.error_msg = response['message']
            else:
                order_result.id = result['response']['order_id']
                order_result.symbol = result['response']['product_id']
                if result['response']['side'] == 'BUY':
                    order_result.side = OrderSide.BUY
                elif result['response']['side'] == 'SELL':
                    order_result.side = OrderSide.SELL

                order_result.status = OrderStatus.PLACED
                order_result.error_reason = OrderErrorReason.NONE

                sub_result = result
        elif 'results' in result:
            if len(result['results']) > 1:
                print("WARNING: Multiple results found (not supported)")
            r = result['results'][0]
            if r['success']:
                order_result.id = r['order_id']
                if r['failure_reason'] == "UNKNOWN_CANCEL_FAILURE_REASON":
                    order_result.status = OrderStatus.CANCELLED
        elif 'order' in result:
            sub_result = result['order']
        
        if sub_result:
            if 'order_id' in sub_result:
                order_result.id = sub_result['order_id']
            if 'product_id' in sub_result:
                order_result.symbol = sub_result['product_id']
    
            # get order side
            if 'side' in sub_result:
                if sub_result['side'] == 'BUY':
                    order_result.side = OrderSide.BUY
                elif sub_result['side'] == 'SELL':
                    order_result.side = OrderSide.SELL
            
            if 'created_time' in sub_result and sub_result['created_time'] is not None:
                # Convert to datetime object
                dt = datetime.fromisoformat(sub_result['created_time'].replace("Z", "+00:00"))
                # Convert to Unix timestamp
                order_result.placed_ts = int(dt.timestamp())

            if 'last_fill_time' in sub_result and sub_result['last_fill_time'] is not None:
                # Convert to datetime object
                dt = datetime.fromisoformat(sub_result['last_fill_time'].replace("Z", "+00:00"))
                # Convert to Unix timestamp
                order_result.filled_ts = int(dt.timestamp())

            if 'filled_size' in sub_result:
                order_result.filled_size = float(sub_result['filled_size'])

            if 'total_fees' in sub_result:
                order_result.fee = float(sub_result['total_fees'])

            if 'time_in_force' in sub_result:
                if sub_result['time_in_force'] == 'GOOD_UNTIL_CANCELLED':
                    order_result.limit_type = OrderLimitType.GTC
                elif sub_result['time_in_force'] == 'IMMEDIATE_OR_CANCEL':
                    order_result.limit_type = OrderLimitType.IOC
                else:
                    order_result.limit_type = OrderLimitType.UNKNOWN

            if 'average_filled_price' in sub_result:
                order_result.price = float(sub_result['average_filled_price'])
            elif 'filled_value' in sub_result:
                order_result.price = float(sub_result['filled_value'])

            if 'order_configuration' in sub_result:
                order_configuration = sub_result['order_configuration']

                if 'market_market_ioc' in order_configuration:
                    order_type = 'market_market_ioc'
                    order_result.type = OrderType.MARKET
                    order_result.size = float(order_configuration[order_type]['base_size'])
                    order_result.status = OrderStatus.PLACED
                    order_result.error_reason = OrderErrorReason.NONE
                elif 'limit_limit_gtc' in order_configuration:
                    order_type = 'limit_limit_gtc'
                    order_result.type = OrderType.LIMIT
                    order_result.limit_price = float(order_configuration[order_type]['limit_price'])
                    order_result.size = float(order_configuration[order_type]['base_size'])
                    order_result.status = OrderStatus.PLACED
                    order_result.error_reason = OrderErrorReason.NONE
                    if 'post_only' in order_configuration[order_type]:
                        order_result.post_only = order_configuration[order_type]['post_only']
                elif 'stop_limit_stop_limit_gtc' in order_configuration:
                    order_type = 'stop_limit_stop_limit_gtc'
                    order_result.type = OrderType.STOP_LOSS_LIMIT
                    order_result.limit_price = float(order_configuration[order_type]['limit_price'])
                    order_result.size = float(order_configuration[order_type]['base_size'])
                    order_result.stop_price = float(order_configuration[order_type]['stop_price'])
                    if order_configuration[order_type]['stop_direction'] == "STOP_DIRECTION_STOP_UP":
                        order_result.stop_direction = OrderStopDirection.ABOVE
                    elif order_configuration[order_type]['stop_direction'] == "STOP_DIRECTION_STOP_DOWN":
                        order_result.stop_direction = OrderStopDirection.BELOW
                    order_result.status = OrderStatus.PLACED
                    order_result.error_reason = OrderErrorReason.NONE
                    if 'post_only' in order_configuration[order_type]:
                        order_result.post_only = order_configuration[order_type]['post_only']
                else:
                    order_result.type = OrderType.UNKNOWN

                if 'status' in sub_result:
                    if sub_result['status'] == 'FILLED':
                        order_result.status = OrderStatus.FILLED
                    elif sub_result['status'] == 'CANCELLED':
                        order_result.status = OrderStatus.CANCELLED
                    elif sub_result['status'] == 'CANCEL_QUEUED':
                        order_result.status = OrderStatus.CANCELLED

        return order_result
