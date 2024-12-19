from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
import ccxt
from cointrader.common.SymbolInfo import SymbolInfo
from cointrader.order.OrderResult import OrderResult
from cointrader.order.enum.OrderStatus import OrderStatus
from cointrader.order.enum.OrderSide import OrderSide
from cointrader.order.enum.OrderType import OrderType
from cointrader.order.enum.OrderLimitType import OrderLimitType
from cointrader.order.enum.OrderStopDirection import OrderStopDirection
from cointrader.order.enum.OrderErrorReason import OrderErrorReason
from datetime import datetime

class CCXTTraderExchange(TraderExchangeBase):
    MAX_CANDLES = 350
    LIMIT = 250
    STOP_DIRECTION_DOWN = "STOP_DIRECTION_STOP_DOWN"
    STOP_DIRECTION_UP = "STOP_DIRECTION_STOP_UP"

    def __init__(self, api_key, api_secret, logger=None):
        self._name = "ccxt"
        self.client = ccxt.coinbaseadvanced({
            'apiKey': api_key,
            'secret': api_secret,
        })
        self.logger = logger
        self._quote_currency_list = ['BTC', 'ETH', 'USDC', 'USD', 'USDT']
        self._excluded_currency_list = ['EUR', 'GBP', 'CDE', 'INTX']
        self._stable_currency_list = ['USD', 'USDC', 'USDT']
        self._equivalent_currency_list = self._stable_currency_list
        self._primary_stable_currency = 'USD'
        self._granularity_mapping = {
            60: '1m',
            300: '5m',
            900: '15m',
            3600: '1h',
            21600: '6h',
            86400: '1d',
        }

    def get_client(self):
        return self.client

    def _ccxt_symbol(self, ticker: str) -> str:
        # Convert from BASE-QUOTE to BASE/QUOTE
        return ticker.replace('-', '/')

    def _internal_ticker_format(self, symbol: str) -> str:
        # Convert from BASE/QUOTE to BASE-QUOTE
        return symbol.replace('/', '-')

    def _info_get_products(self):
        # Fetch all markets
        markets = self.client.fetch_markets()
        products = []
        for m in markets:
            base = m['base']
            quote = m['quote']
            product_id = f"{base}-{quote}"
            excluded = False
            for exclude in self._excluded_currency_list:
                if product_id.endswith(f"-{exclude}"):
                    excluded = True
                    break
            if excluded:
                continue
            # Simulate a product object similar to coinbase advanced format
            product = {
                'product_id': product_id,
                'base_currency_id': base,
                'quote_currency_id': quote,
                'trading_disabled': not m['active'],
                # CCXT doesn't provide 'price' in market object, we may fetch ticker later if needed
                'price': None, 
                'base_min_size': m['limits']['amount']['min'] if m['limits']['amount'] else 0,
                'base_increment': m['precision']['amount'] if m['precision']['amount'] is not None else 0,
                'quote_min_size': m['limits']['cost']['min'] if m['limits']['cost'] else 0,
                'quote_increment': m['precision']['price'] if m['precision']['price'] is not None else 0
            }
            products.append(product)
        return products

    def _info_get_accounts(self):
        # Fetch all balances (accounts)
        balance = self.client.fetch_balance()
        # Create a pseudo account object
        accounts = []
        for currency, data in balance['total'].items():
            account = {
                'currency': currency,
                'available_balance': {'value': balance['free'][currency]} if currency in balance['free'] else {'value': 0.0},
                'hold': {'value': balance['used'][currency]} if currency in balance['used'] else {'value': 0.0}
            }
            accounts.append(account)
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
        products = self._info_get_products()
        result = []
        for product in products:
            if product['base_currency_id'] not in result:
                result.append(product['base_currency_id'])
        return result

    def info_quote_currencies_list(self) -> list[str]:
        """Return list of all quote currency names"""
        return self._quote_currency_list

    def info_ticker_names_list(self) -> list[str]:
        """Return list of all ticker names"""
        products = self._info_get_products()
        result = []
        for product in products:
            if product['quote_currency_id'] in self._excluded_currency_list:
                continue
            result.append(product['product_id'])
        return result

    def info_ticker_join(self, base: str, quote: str) -> str:
        """Create a ticker from base and quote currency names"""
        return f"{base}-{quote}"

    def info_ticker_split(self, ticker: str) -> tuple[str, str]:
        """Split ticker into base and quote currency names"""
        return tuple(ticker.split('-'))

    def info_ticker_query(self, ticker: str) -> SymbolInfo:
        """Query ticker information (symbol details)"""
        products = self._info_get_products()
        product = next((p for p in products if p['product_id'] == ticker), None)
        if product is None:
            # If not found, try fetch_ticker for price
            # Just fill minimal info
            symbol = self._ccxt_symbol(ticker)
            ticker_data = self.client.fetch_ticker(symbol)
            base, quote = self.info_ticker_split(ticker)
            product = {
                'product_id': ticker,
                'base_currency_id': base,
                'quote_currency_id': quote,
                'price': ticker_data['last'],
                'base_min_size': 0.0,
                'base_increment': 0.0,
                'quote_min_size': 0.0,
                'quote_increment': 0.0
            }
        return self.info_ticker_parse(ticker, product)

    def info_ticker_parse(self, ticker: str, response) -> SymbolInfo:
        """Parse ticker information from product info"""
        result = SymbolInfo()
        result.base_name = response['base_currency_id']
        result.quote_name = response['quote_currency_id']
        if response['price']:
            result.price = float(response['price'])
        else:
            # fetch ticker price if not available
            symbol = self._ccxt_symbol(ticker)
            ticker_data = self.client.fetch_ticker(symbol)
            result.price = ticker_data['last'] if ticker_data['last'] is not None else 0.0

        result.base_min_size = float(response['base_min_size'])
        # base_step_size might be derived from precision info
        result.base_step_size = 10 ** (-response['base_increment']) if isinstance(response['base_increment'], int) else float(response['base_increment'])
        result.quote_min_size = float(response['quote_min_size'])
        result.quote_step_size = 10 ** (-response['quote_increment']) if isinstance(response['quote_increment'], int) else float(response['quote_increment'])

        def get_precision(step_size: float) -> int:
            step_size_str = f"{step_size:.10f}".rstrip('0')
            if '.' in step_size_str:
                return len(step_size_str.split('.')[1])
            return 0

        result.base_precision = get_precision(result.base_step_size)
        result.quote_precision = get_precision(result.quote_step_size)

        return result

    def info_ticker_query_all(self) -> dict[str, SymbolInfo]:
        """Query all tickers"""
        result = {}
        products = self._info_get_products()
        for product in products:
            if product['trading_disabled']:
                continue
            if product['quote_currency_id'] in self._excluded_currency_list:
                continue
            symbol_info = self.info_ticker_parse(product['product_id'], product)
            result[product['product_id']] = symbol_info
        return result

    def info_currency_query(self, currency: str) -> dict:
        """Query currency information"""
        # Not implemented in ccxt generically
        raise NotImplementedError

    def account_get_ids(self) -> dict:
        """Get account ids if account is multi-account"""
        raise NotImplementedError

    def account_get_maker_fee(self) -> float:
        """Get maker fee"""
        # Some exchanges support fetchTradingFee or fetchTradingFees
        # For coinbasepro, we can try:
        trading_fees = self.client.fetch_trading_fees()
        # fees are typically by tier; assume 'maker' in structure
        return trading_fees.get('maker', 0.0)

    def account_get_taker_fee(self) -> float:
        """Get taker fee"""
        trading_fees = self.client.fetch_trading_fees()
        return trading_fees.get('taker', 0.0)

    def balance_get(self, currency: str) -> tuple[float, float]:
        """Get balance of currency"""
        balance = self.client.fetch_balance()
        free = balance['free'].get(currency, 0.0)
        used = balance['used'].get(currency, 0.0)
        return (free, used)

    def balance_set(self, currency: str, available: float, hold: float) -> None:
        """Set balance of currency (used for testing)"""
        pass

    def balance_all_get(self) -> dict[str, tuple[float, float]]:
        """Get all balances"""
        balance = self.client.fetch_balance()
        result = {}
        for c in balance['total']:
            result[c] = (balance['free'][c], balance['used'][c])
        return result

    def market_ticker_price_get(self, ticker: str) -> float:
        """Get ticker price"""
        symbol = self._ccxt_symbol(ticker)
        t = self.client.fetch_ticker(symbol)
        return t['last'] if t['last'] is not None else 0.0

    def market_ticker_prices_all_get(self) -> dict:
        """Get all ticker prices"""
        # We can fetch all markets and then fetch tickers
        products = self._info_get_products()
        all_tickers = self.client.fetch_tickers()
        result = {}
        for product in products:
            symbol = self._ccxt_symbol(product['product_id'])
            ticker_data = all_tickers.get(symbol, {})
            price = ticker_data.get('last', 0.0)
            result[product['product_id']] = price if price is not None else 0.0
        return result

    def market_get_orderbook(self, ticker: str, level: int) -> dict: 
        """Get orderbook"""
        symbol = self._ccxt_symbol(ticker)
        orderbook = self.client.fetch_order_book(symbol, limit=level)
        return orderbook

    def market_get_trades(self, ticker: str, limit: int) -> dict:
        """Get trades for ticker"""
        symbol = self._ccxt_symbol(ticker)
        trades = self.client.fetch_trades(symbol, limit=limit)
        return trades

    def market_get_kline_granularities(self) -> list[int]:
        """Get kline granularities"""
        return list(self._granularity_mapping.keys())

    def market_get_max_kline_count(self, granularity: int) -> int:
        return self.MAX_CANDLES

    def market_get_klines_range(self, ticker: str, start_ts: int, end_ts: int, granularity: int) -> list:
        """Get klines for a given interval"""
        symbol = self._ccxt_symbol(ticker)
        timeframe = self._granularity_mapping[granularity]
        # Convert seconds to milliseconds
        since = start_ts * 1000
        # We'll guess how many candles we might need based on difference
        # CCXT fetch_ohlcv limit defaults vary by exchange. We'll just fetch max_candles.
        candles = self.client.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=self.MAX_CANDLES)
        # CCXT returns: [timestamp, open, high, low, close, volume]
        # Convert to similar structure as original code
        result = []
        for c in candles:
            candle_dict = {
                'start_time': c[0],
                'open': c[1],
                'high': c[2],
                'low': c[3],
                'close': c[4],
                'volume': c[5]
            }
            result.append(candle_dict)
        return result

    def trade_buy_market(self, ticker: str, amount: float) -> dict:
        symbol = self._ccxt_symbol(ticker)
        try:
            order = self.client.create_order(symbol, 'market', 'buy', amount)
            return self.trade_parse_order_result(order, ticker)
        except Exception as e:
            return self.trade_parse_order_result({'error': str(e)}, ticker)

    def trade_sell_market(self, ticker: str, amount: float) -> dict:
        symbol = self._ccxt_symbol(ticker)
        try:
            order = self.client.create_order(symbol, 'market', 'sell', amount)
            return self.trade_parse_order_result(order, ticker)
        except Exception as e:
            return self.trade_parse_order_result({'error': str(e)}, ticker)

    def trade_buy_limit(self, ticker: str, amount: float, price: float, type: str = "") -> dict:
        symbol = self._ccxt_symbol(ticker)
        try:
            order = self.client.create_order(symbol, 'limit', 'buy', amount, price)
            return self.trade_parse_order_result(order, ticker)
        except Exception as e:
            return self.trade_parse_order_result({'error': str(e)}, ticker)

    def trade_sell_limit(self, ticker: str, amount: float, price: float, type: str = "") -> dict:
        symbol = self._ccxt_symbol(ticker)
        try:
            order = self.client.create_order(symbol, 'limit', 'sell', amount, price)
            return self.trade_parse_order_result(order, ticker)
        except Exception as e:
            return self.trade_parse_order_result({'error': str(e)}, ticker)

    def trade_buy_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float,
                             stop_direction: OrderStopDirection = OrderStopDirection.ABOVE, type: str = "") -> dict:
        # Not all exchanges support advanced stop limit orders directly via CCXT.
        # For coinbasepro, stop orders might be placed with params.
        # Example (for coinbasepro): params = {'stop': 'entry', 'stopPrice': stop_price}
        symbol = self._ccxt_symbol(ticker)
        direction = 'up' if stop_direction == OrderStopDirection.ABOVE else 'down'
        try:
            params = {
                'stop': 'entry',
                'stopPrice': stop_price
            }
            order = self.client.create_order(symbol, 'limit', 'buy', amount, price, params)
            return self.trade_parse_order_result(order, ticker)
        except Exception as e:
            return self.trade_parse_order_result({'error': str(e)}, ticker)

    def trade_sell_stop_limit(self, ticker: str, amount: float, price: float, stop_price: float,
                              stop_direction: OrderStopDirection = OrderStopDirection.BELOW, type: str = "") -> dict:
        symbol = self._ccxt_symbol(ticker)
        direction = 'down' if stop_direction == OrderStopDirection.BELOW else 'up'
        try:
            params = {
                'stop': 'entry',
                'stopPrice': stop_price
            }
            order = self.client.create_order(symbol, 'limit', 'sell', amount, price, params)
            return self.trade_parse_order_result(order, ticker)
        except Exception as e:
            return self.trade_parse_order_result({'error': str(e)}, ticker)

    def trade_cancel_order(self, ticker: str, order_id: str) -> dict:
        symbol = self._ccxt_symbol(ticker)
        try:
            result = self.client.cancel_order(order_id, symbol)
            return self.trade_parse_order_result(result, ticker)
        except Exception as e:
            return self.trade_parse_order_result({'error': str(e)}, ticker)

    def trade_get_order(self, ticker: str, order_id: str) -> dict:
        symbol = self._ccxt_symbol(ticker)
        try:
            order = self.client.fetch_order(order_id, symbol)
            return self.trade_parse_order_result(order, ticker)
        except Exception as e:
            return self.trade_parse_order_result({'error': str(e)}, ticker)

    def trade_get_open_orders(self, ticker: str) -> dict:
        symbol = self._ccxt_symbol(ticker)
        orders = self.client.fetch_open_orders(symbol)
        # Return a list of parsed orders
        return {'orders': [self.trade_parse_order_result(o, ticker) for o in orders]}

    def trade_get_closed_orders(self, ticker: str) -> dict:
        symbol = self._ccxt_symbol(ticker)
        orders = self.client.fetch_closed_orders(symbol)
        return {'orders': [self.trade_parse_order_result(o, ticker) for o in orders]}

    def trade_parse_order_result(self, result, ticker: str) -> OrderResult:
        """Parse order result from ccxt order structure."""
        order_result = OrderResult(symbol=ticker)

        # If there's an error dict:
        if isinstance(result, dict) and 'error' in result:
            order_result.status = OrderStatus.REJECTED
            order_result.error_reason = OrderErrorReason.UNKNOWN
            order_result.error_msg = result['error']
            return order_result

        # ccxt unified order structure:
        # {
        #   'id': '12345',
        #   'clientOrderId': None,
        #   'timestamp': 1640342400000,
        #   'datetime': '2021-12-24T00:00:00Z',
        #   'lastTradeTimestamp': None,
        #   'symbol': 'BTC/USD',
        #   'type': 'limit',
        #   'timeInForce': 'GTC',
        #   'postOnly': False,
        #   'side': 'buy',
        #   'price': 40000.0,
        #   'amount': 0.1,
        #   'filled': 0.0,
        #   'remaining': 0.1,
        #   'cost': 0.0,
        #   'trades': [],
        #   'fee': {'cost': 0.0, 'currency': 'USD'},
        #   'status': 'open' or 'closed' or 'canceled'
        # }

        o = result
        order_result.id = o.get('id', None)
        # Convert symbol back if needed
        if 'symbol' in o and o['symbol']:
            order_result.symbol = self._internal_ticker_format(o['symbol'])

        side = o.get('side')
        if side == 'buy':
            order_result.side = OrderSide.BUY
        elif side == 'sell':
            order_result.side = OrderSide.SELL

        order_type = o.get('type')
        if order_type == 'market':
            order_result.type = OrderType.MARKET
        elif order_type == 'limit':
            order_result.type = OrderType.LIMIT
        else:
            order_result.type = OrderType.UNKNOWN

        # Time in force mapping is not always provided by CCXT
        tif = o.get('timeInForce', 'GTC')
        if tif == 'GTC':
            order_result.limit_type = OrderLimitType.GTC
        elif tif == 'IOC':
            order_result.limit_type = OrderLimitType.IOC
        elif tif == 'FOK':
            order_result.limit_type = OrderLimitType.FOK
        else:
            order_result.limit_type = OrderLimitType.UNKNOWN

        order_result.post_only = o.get('postOnly', False)

        if 'timestamp' in o and o['timestamp'] is not None:
            order_result.placed_ts = int(o['timestamp'] / 1000)
        if 'lastTradeTimestamp' in o and o['lastTradeTimestamp'] is not None:
            order_result.filled_ts = int(o['lastTradeTimestamp'] / 1000)

        order_result.size = float(o.get('amount', 0.0))
        order_result.filled_size = float(o.get('filled', 0.0))
        # price or average?
        order_result.price = float(o.get('price', 0.0))
        fee = o.get('fee', {})
        order_result.fee = float(fee.get('cost', 0.0))

        # Map status
        # ccxt: 'open', 'closed', 'canceled', 'pending'
        # map to OrderStatus
        status = o.get('status', 'unknown')
        if status == 'open':
            order_result.status = OrderStatus.PLACED
        elif status == 'closed':
            # closed usually means fully filled
            if order_result.filled_size >= order_result.size:
                order_result.status = OrderStatus.FILLED
            else:
                # partially filled then closed? treat as FILLED
                order_result.status = OrderStatus.FILLED
        elif status == 'canceled':
            order_result.status = OrderStatus.CANCELLED
        elif status == 'pending':
            order_result.status = OrderStatus.PENDING
        else:
            order_result.status = OrderStatus.UNKNOWN

        order_result.error_reason = OrderErrorReason.NONE

        return order_result
