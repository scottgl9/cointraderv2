from cointrader.account.CryptoAccountBase import CryptoAccountBase
#from cointrader.lib.struct.TraderMessage import TraderMessage
#from cointrader.lib.struct.Order import Order
#from cointrader.lib.struct.OrderUpdate import OrderUpdate
#from cointrader.lib.struct.SymbolInfo import SymbolInfo
#from cointrader.lib.struct.Exchange import Exchange
from .AccountCoinbaseInfo import AccountCoinbaseInfo
from .AccountCoinbaseBalance import AccountCoinbaseBalance
from .AccountCoinbaseTrade import AccountCoinbaseTrade
from .AccountCoinbaseMarket import AccountCoinbaseMarket
from coinbase.rest import RESTBase, RESTClient
from cointrader.config import *
import json
import os
import time
from datetime import datetime, timedelta
import aniso8601
import stix.utils.dates
import logging


class AccountCoinbaseAdvanced(CryptoAccountBase):
    def __init__(self, client=None, simulate=False, live=False, logger=None, simulate_db_filename=None):
        super(AccountCoinbaseAdvanced, self).__init__(client, simulate, live, logger, simulate_db_filename)
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger
        self.simulate = simulate
        self.live = live
        self.simulate_db_filename = simulate_db_filename
        if client is not None:
            self.client = client
        elif not self.simulate:
            client = RESTClient(api_key=CBADV_KEY, api_secret=CBADV_SECRET)
            self.client = client

        # sub module implementations
        self.info = AccountCoinbaseInfo(client, simulate, logger)
        self.trade = AccountCoinbaseTrade(client, self.info, simulate, logger)
        self.market = AccountCoinbaseMarket(client, self.info, simulate, logger)
        self.balance = AccountCoinbaseBalance(client, self.info, self.market, simulate, logger)

        # hourly db column names
        self.hourly_cnames = ['ts', 'low', 'high', 'open', 'close', 'volume']

        # keep track of initial currency buy size, and subsequent trades against currency
        self._currency_buy_size = {}
        for currency in self.info.get_currencies():
            self._currency_buy_size[currency] = 0

        self._trader_profit_mode = 'BTC'
        self._tpprofit = 0
        self.initial_currency = 0
        self.loaded_model_count = 0

    # if hourly table name doesn't match symbol name
    # ex. symbol 'BTC-USD', db table name 'BTC_USD'
    def get_hourly_table_name(self, symbol):
        return symbol.replace('-', '_')

    # get symbol name from hourly table name
    # ex. table name 'BTC_USD', return symbol 'BTC-USD'
    def get_symbol_hourly_table(self, table_name):
        return table_name.replace('_', '-')

    # get hourly db column names
    def get_hourly_column_names(self):
        return self.hourly_cnames

    def set_trader_profit_mode(self, mode):
        if mode in self.info.get_currencies():
            self._trader_profit_mode = mode
        else:
            self.logger.info("set_trader_profit_mode({}) FAILED".format(mode))

    def get_trader_profit_mode(self):
        return self._trader_profit_mode

    def set_total_percent_profit(self, tpprofit):
        self._tpprofit = tpprofit

    def get_total_percent_profit(self):
        return self._tpprofit

    def get_currency_buy_size(self, name):
        if not self.is_currency(name):
            return 0
        return self._currency_buy_size[name]

    def set_currency_buy_size(self, name, size=0):
        if not self.is_currency(name):
            return 0
        self._currency_buy_size[name] = size

    # buy_size is amount of currency used to buy an asset
    # sell_size is amount of currency retrieved by selling asset
    def update_currency_buy_size(self, name, asset_buy_size=0, asset_sell_size=0):
        if not self.is_currency(name):
            return 0
        if asset_buy_size:
            self._currency_buy_size[name] -= asset_buy_size
        if asset_sell_size:
            self._currency_buy_size[name] += asset_sell_size
        return self._currency_buy_size[name]

    # determine if asset is available (not disabled or delisted)
    # if not, don't trade
    def is_asset_available(self, name):
        status = self.get_asset_status(name)
        try:
            if status['disabled']:
                return False
            if status['delisted']:
                return False
        except KeyError:
            return False
        return True

    def cancel_all(self, ticker_id=None):
        return self.client.cancel_all(product_id=ticker_id)
