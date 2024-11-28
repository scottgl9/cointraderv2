#from cointrader.lib.struct.Order import Order
#from cointrader.lib.struct.Exchange import Exchange
#from cointrader.lib.struct.SymbolInfo import SymbolInfo
import math


class CryptoAccountBase(object):
    def __init__(self, client, simulate=False, live=False, logger=None, simulate_db_filename=None):
        self.logger = logger
        self.simulate_db_filename = simulate_db_filename
        self.client = client
        self.simulate = simulate
        self.live = live
        #self.exchange_type = Exchange.EXCHANGE_UNKNOWN

        # account specific components
        self.info = None
        self.balance = None
        self.trade = None
        self.market = None

    def get_config_section_name(self):
        pass

    def ts_to_seconds(self, ts):
        pass

    def is_hourly_ts(self, ts):
        pass

    def get_hourly_ts(self, ts):
        pass

    def seconds_to_ts(self, seconds):
        pass

    def hours_to_ts(self, hours):
        pass

    def get_hourly_table_name(self, symbol):
        pass

    def get_symbol_hourly_table(self, table_name):
        pass

    def get_hourly_column_names(self):
        pass

    def _round_down(self, value, decimals):
        factor = 10 ** decimals
        return math.floor(value * factor) / factor

    def round_base(self, price, base_increment=0):
        if base_increment:
            try:
                precision = '{:.8f}'.format(float(base_increment)).index('1')
                if float(base_increment) < 1.0:
                    precision -= 1
            except ValueError:
                self.logger.warning("round_base(): index not found in {}, price={}".format(base_increment, price))
                return price

            return round(float(price), precision)
        return price

    def round_quote(self, price, quote_increment=0):
        if quote_increment:
            try:
                precision = '{:.8f}'.format(float(quote_increment)).index('1')
                if float(quote_increment) < 1.0:
                    precision -= 1
            except ValueError:
                self.logger.warning("round_quote(): index not found in {}, price={}".format(quote_increment, price))
                return price
            return round(float(price), precision)
        return price

    def round_quantity(self, size, min_qty=0):
        if min_qty:
            try:
                precision = '{:.8f}'.format(float(min_qty)).index('1')
                if float(min_qty) < 1.0:
                    precision -= 1
            except ValueError:
                self.logger.warning("round_quantity(): index not found in {}, size={}".format(min_qty, size))
                return size
            return self._round_down(float(size), precision)
        return size

    def round_base_symbol(self, symbol, price):
        base_increment = self.get_symbol_info_dict(symbol=symbol, field='base_step_size')
        return self.round_base(price, base_increment)

    def round_quantity_symbol(self, symbol, size):
        min_qty = self.get_symbol_info_dict(symbol=symbol, field='min_qty')
        return self.round_quantity(size, min_qty)

    def round_quote_symbol(self, symbol, price):
        quote_increment = self.get_symbol_info_dict(symbol=symbol, field='currency_step_size')
        return self.round_quote(price, quote_increment)

    def round_quote_pair(self, base, currency, price):
        quote_increment = self.get_symbol_info_dict(base=base, currency=currency, field='currency_step_size')
        return self.round_quote(price, quote_increment)

    def my_float(self, value):
        if float(value) >= 0.1:
            return "{}".format(float(value))
        else:
            return "{:.8f}".format(float(value))

    def get_base_step_size(self, symbol=None, base=None, currency=None):
        info = self.get_symbol_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return 0
        return info['base_step_size']

    def get_currency_step_size(self, symbol=None, base=None, currency=None):
        info = self.get_symbol_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return 0
        return info['currency_step_size']

    def split_symbol(self, symbol):
        return self.split_ticker_id(symbol)

    def get_symbol_base(self, symbol):
        result = self.split_ticker_id(symbol)
        if result:
            return result[0]
        return None

    def get_symbol_currency(self, symbol):
        result = self.split_ticker_id(symbol)
        if result:
            return result[1]
        return None

    def is_currency(self, name):
        if name in self.info.get_currencies():
            return True
        return False

    def is_currency_pair(self, symbol=None, base=None, currency=None):
        return self.info.is_currency_pair(symbol, base, currency)

    # 'info' component functions
    def make_ticker_id(self, base, currency):
        return self.info.make_ticker_id(base, currency)

    def split_ticker_id(self, symbol):
        return self.info.split_ticker_id(symbol)

    def get_config_section_name(self):
        return self.info.get_config_section_name()

    def get_trader_mode(self):
        return self.info.get_trader_mode()

    def set_trader_mode(self, trader_mode):
        return self.info.set_trader_mode(trader_mode)

    def get_account_mode(self):
        return self.info.get_account_mode()

    def set_account_mode(self, account_mode):
        return self.info.set_account_mode(account_mode)

    # fractional trade fee
    def get_trade_fee(self):
        return self.info.get_trade_fee()

    def get_currencies(self):
        return self.info.get_currencies()

    def get_info_all_pairs(self):
        return self.info.get_info_all_pairs()

    def get_info_all_assets(self):
        return self.info.get_info_all_assets()

    def format_ts(self, ts):
        return self.info.format_ts(ts)

    def ts_to_seconds(self, ts):
        return self.info.ts_to_seconds(ts)

    def is_hourly_ts(self, ts):
        return self.info.is_hourly_ts(ts)

    def get_hourly_ts(self, ts):
        return self.info.get_hourly_ts(ts)

    def seconds_to_ts(self, seconds):
        return self.info.seconds_to_ts(seconds)

    def hours_to_ts(self, hours):
        return self.info.hours_to_ts(hours)

    def load_exchange_info(self):
        return self.info.load_exchange_info()

    def get_exchange_info(self):
        return self.info.get_exchange_info()

    def parse_exchange_info(self, pair_info, symbol_info):
        return self.info.parse_exchange_info(pair_info, symbol_info)

    def get_exchange_pairs(self):
        return self.info.get_exchange_pairs()

    def is_exchange_pair(self, symbol):
        return self.info.is_exchange_pair(symbol)

    def get_asset_status(self, name=None):
        return self.info.get_asset_status(name)

    def get_symbol_info(self, symbol=None, base=None, currency=None):
        return self.info.get_symbol_info(symbol, base, currency)

    def get_symbol_info_dict(self, symbol=None, base=None, currency=None, field=None) -> dict:
        return self.info.get_symbol_info_dict(symbol, base, currency, field)

    def is_asset_available(self, name):
        return self.info.is_asset_available(name)

    # 'balance' component functions
    def get_account_total_value(self, currency, detailed=False):
        return self.balance.get_account_total_value(currency, detailed)

    def get_account_balances(self, detailed=False):
        return self.balance.get_account_balances(detailed)

    def get_balances(self):
        return self.balance.get_balances()

    def get_asset_balance(self, asset):
        return self.balance.get_asset_balance(asset)

    def get_asset_balance_tuple(self, asset):
        return self.balance.get_asset_balance_tuple(asset)

    def update_asset_balance(self, name, balance, available):
        return self.balance.update_asset_balance(name, balance, available)

    # 'trade' component functions
    def buy_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            return self.buy_market_simulate(size, price, ticker_id)
        else:
            return self.trade.buy_market(size, price, ticker_id)

    def sell_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            return self.sell_market_simulate(size, price, ticker_id)
        else:
            return self.trade.sell_market(size, price, ticker_id)

    def buy_limit(self, price, size, ticker_id=None):
        if self.simulate:
            return self.buy_limit_simulate(price, size, ticker_id)
        else:
            return self.trade.buy_limit(size, price, ticker_id)

    def sell_limit(self, price, size, ticker_id=None):
        if self.simulate:
            return self.sell_limit_simulate(size, price, ticker_id)
        else:
            return self.trade.sell_limit(size, price, ticker_id)

    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            return self.buy_limit_stop_simulate(price, size, stop_price, ticker_id)
        else:
            return self.trade.buy_limit_stop(price, size, stop_price, ticker_id)

    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            return self.sell_limit_stop_simulate(price, size, stop_price, ticker_id)
        else:
            return self.trade.sell_limit_stop(price, size, stop_price, ticker_id)

    # simulate buy market order
    def buy_market_simulate(self, size, price=0.0, ticker_id=None):
        size = self.round_base_symbol(ticker_id, size)
        base, currency = self.split_ticker_id(ticker_id)
        bbalance, bavailable = self.get_asset_balance_tuple(base)
        cbalance, cavailable = self.get_asset_balance_tuple(currency)
        amount = self.round_quote_symbol(ticker_id, float(price) * float(size))
        if amount > cavailable:
            return False

        self.update_asset_balance(base, bbalance + float(size), bavailable + float(size))
        self.update_asset_balance(currency, cbalance - amount, cavailable - amount)
        return True

    # simulate sell market order
    def sell_market_simulate(self, size, price=0.0, ticker_id=None):
        base, currency = self.split_ticker_id(ticker_id)
        bbalance, bavailable = self.get_asset_balance_tuple(base)
        cbalance, cavailable = self.get_asset_balance_tuple(currency)

        if float(size) > bavailable:
            #if self.logger:
            #    self.logger.warning("{}: {} > {}".format(ticker_id, float(size), bavailable))
            return False

        amount = self.round_quote_symbol(ticker_id, float(price) * float(size))
        self.update_asset_balance(base, float(bbalance) - float(size), float(bavailable) - float(size))
        self.update_asset_balance(currency, cbalance + amount, cavailable + amount)
        return True

    # simulate buy limit order
    def buy_limit_simulate(self, price, size, ticker_id=None):
        base, currency = self.split_ticker_id(ticker_id)
        cbalance, cavailable = self.get_asset_balance_tuple(currency)
        usd_value = float(price) * float(size)  # self.round_quote(price * size)

        if usd_value > cavailable: return

        self.update_asset_balance(currency, cbalance, cavailable - usd_value)

    # simulate sell limit order
    def sell_limit_simulate(self, price, size, ticker_id=None):
        base, currency = self.split_ticker_id(ticker_id)
        bbalance, bavailable = self.get_asset_balance_tuple(base)

        if float(size) > bavailable: return

        self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))

    # simulate buy limit stop order
    def buy_limit_stop_simulate(self, price, size, stop_price, ticker_id=None):
        base, currency = self.split_ticker_id(ticker_id)
        cbalance, cavailable = self.get_asset_balance_tuple(currency)
        usd_value = float(price) * float(size)  # self.round_quote(price * size)

        if usd_value > cavailable: return False

        self.update_asset_balance(currency, cbalance, cavailable - usd_value)
        return True

    # simulate sell limit stop order
    def sell_limit_stop_simulate(self, price, size, stop_price, ticker_id=None):
        # self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
        base, currency = self.split_ticker_id(ticker_id)
        bbalance, bavailable = self.get_asset_balance_tuple(base)

        if float(size) > bavailable: return False

        self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
        return True

    # use for both limit orders and stop loss orders
    def buy_limit_complete(self, price, size, ticker_id, simulate):
        if simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = float(price) * float(size) #self.round_quote(price * size)
            if usd_value > cbalance: return False
            #print("buy_market({}, {}, {}".format(size, price, ticker_id))
            self.update_asset_balance(base, bbalance + float(size), bavailable + float(size))
            self.update_asset_balance(currency, cbalance - usd_value, cavailable)
            return True
        else:
            self.get_account_balances()

    # use for both limit orders and stop loss orders
    def sell_limit_complete(self, price, size, ticker_id, simulate):
        if simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)

            if float(size) > bbalance: return False

            usd_value = float(price) * float(size)
            self.update_asset_balance(base, float(bbalance) - float(size), float(bavailable))
            self.update_asset_balance(currency, cbalance + usd_value, cavailable + usd_value)
            return True
        else:
            self.get_account_balances()

    # for handling a canceled sell order during simulation
    def cancel_sell_limit_complete(self, size, ticker_id):
        #if not self.simulate:
        #    return
        base, currency = self.split_ticker_id(ticker_id)
        bbalance, bavailable = self.get_asset_balance_tuple(base)
        self.update_asset_balance(base, float(bbalance), float(bavailable) + float(size))

    def get_order(self, order_id, ticker_id):
        if not self.simulate:
            return self.trade.get_order(order_id, ticker_id)

    def get_orders(self, ticker_id=None):
        if not self.simulate:
            return self.trade.get_orders(ticker_id)

    def cancel_order(self, orderid, ticker_id=None):
        if not self.simulate:
            return self.trade.cancel_order(orderid, ticker_id)

    def parse_order_update(self, result):
        return self.trade.parse_order_update(result)

    # parse json response to order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        return self.trade.parse_order_result(result, symbol, sigid)

    # 'market' component functions
    def get_ticker(self, symbol):
        return self.market.get_ticker(symbol)

    def get_tickers(self):
        return self.market.get_tickers()

    def get_ticker_symbols(self, currency=None):
        return self.market.get_ticker_symbols(currency)

    def get_min_tickers(self):
        return self.market.get_min_tickers()

    def get_max_tickers(self):
        return self.market.get_max_tickers()

    def update_ticker(self, symbol, price, ts):
        return self.market.update_ticker(symbol, price, ts)

    def update_tickers(self, tickers):
        return self.market.update_tickers(tickers)

    def get_klines(self, days=0, hours=1, mode=None, ticker_id=None, granularity=3600):
        return self.market.get_klines(days, hours, mode, ticker_id)

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        return self.market.get_hourly_klines(symbol, start_ts, end_ts)
