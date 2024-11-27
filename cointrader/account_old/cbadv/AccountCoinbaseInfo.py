import os
import json
from cointrader.account.CryptoAccountBaseInfo import CryptoAccountBaseInfo
#from cointrader.lib.struct.Order import Order
#from cointrader.lib.struct.AssetInfo import AssetInfo
#from cointrader.lib.struct.Exchange import Exchange
from coinbase.rest import RESTClient


class AccountCoinbaseInfo(CryptoAccountBaseInfo):
    def __init__(self, client : RESTClient, simulate=False, logger=None):
        self.client = client
        self.simulate = simulate
        self.logger = logger
        #self.exchange_type = Exchange.EXCHANGE_CBADV
        self.exchange_name = "CBADV"#Exchange.name(self.exchange_type)
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.info_all_pairs = {}
        self.info_all_assets = {}
        self._exchange_pairs = None
        # hourly db column names
        self.hourly_cnames = ['ts', 'low', 'high', 'open', 'close', 'volume']
        self.currencies = ['BTC', 'ETH', 'USDC', 'USD']
        self.currency_trade_pairs = ['ETH-BTC', 'BTC-USDC', 'ETH-USDC', 'BTC-USD', 'ETH-USD']
        self.trade_fee = 0.5 / 100.0
        #self._trader_mode = Exchange.TRADER_MODE_NONE
        #self._account_mode = Exchange.ACCOUNT_MODE_CRYPTO

    def make_ticker_id(self, base, currency):
        return '%s-%s' % (base, currency)

    def split_ticker_id(self, symbol):
        base_name = None
        currency_name = None

        parts = symbol.split('-')
        if len(parts) == 2:
            base_name = parts[0]
            currency_name = parts[1]

        return base_name, currency_name

    # get config section name from trader.ini
    def get_config_section_name(self):
        if self.simulate:
            name = "{}.simulate".format(self.exchange_name)
        else:
            name = "{}.live".format(self.exchange_name)
        return name

    def get_trader_mode(self):
        return self._trader_mode

    def set_trader_mode(self, trader_mode):
        self._trader_mode = trader_mode

    def get_account_mode(self):
        return self._account_mode

    def set_account_mode(self, account_mode):
        self._account_mode = account_mode

    def get_trade_fee(self):
        return self.trade_fee

    def get_currencies(self):
        return self.currencies

    def get_currency_trade_pairs(self):
        return self.currency_trade_pairs

    def get_info_all_pairs(self):
        return self.info_all_pairs

    def get_info_all_assets(self):
        return self.info_all_assets

    def format_ts(self, ts):
        return int(ts)

    def ts_to_seconds(self, ts):
        return float(ts)

    # returns true if this ts is an hourly ts
    def is_hourly_ts(self, ts):
        hourly_ts = self.get_hourly_ts(ts)
        return int(ts) == hourly_ts

    # set minutes and seconds components of timestamp to zero
    def get_hourly_ts(self, ts):
        #dt = datetime.utcfromtimestamp(self.ts_to_seconds(ts)).replace(minute=0, second=0)
        #return int(self.seconds_to_ts(time.mktime(dt.timetuple())))
        return int(self.ts_to_seconds(ts) / 3600.0) * 3600

    def seconds_to_ts(self, seconds):
        return float(seconds)

    def hours_to_ts(self, hours):
        return float(hours * 3600)

    # For simulation: load exchange info from file, or call get_exchange_info() and save to file
    def load_exchange_info(self):
        if not self.simulate and os.path.exists(self.exchange_info_file):
            info = self.get_exchange_info()
            self.info_all_pairs = info['pairs']
            self.info_all_assets = info['assets']
            return

        print(self.exchange_info_file)
        if not os.path.exists(self.exchange_info_file):
            info = self.get_exchange_info()
            with open(self.exchange_info_file, 'w') as f:
                info['pairs'] = dict(sorted(info['pairs'].items()))
                info['assets'] = dict(sorted(info['assets'].items()))
                json.dump(info, f, indent=4)
        else:
            info = json.loads(open(self.exchange_info_file).read())
        self.info_all_pairs = info['pairs']
        self.info_all_assets = info['assets']

    # get exchange info from exchange via API
    def get_exchange_info(self):
        pair_info = self.client.get_products(limit=250).products
        asset_info = None
        return self.parse_exchange_info(pair_info, asset_info)

    def parse_exchange_info(self, pair_info, asset_info):
        """
        :type pair_info: list[Product]
        """
        exchange_info = {}
        pairs = {}
        assets = {}

        for info in pair_info:
            symbol = info.product_id
            base_step_size =  info.base_increment
            currency_step_size = info.quote_increment
            base_precision = abs(int('{:e}'.format(float(base_step_size)).split('e')[-1]))
            currency_precision = abs(int('{:e}'.format(float(currency_step_size)).split('e')[-1]))
            pairs[symbol] = {'min_qty': info.base_min_size,
                             'min_price': info.quote_min_size,
                             'base_step_size': base_step_size,
                             'currency_step_size': currency_step_size,
                             'base_precision': base_precision,
                             'currency_precision': currency_precision
                            }
            
            if info.is_disabled or info.trading_disabled or info.view_only:
                assets[info.base_currency_id] = {'disabled': True, 'delisted': False }
            else:
                assets[info.base_currency_id] = {'disabled': False, 'delisted': False }

        self._exchange_pairs = []

        for pair in pairs.keys():
            # ignore trade pairs with GBP and EUR currency
            if pair.endswith('GBP') or pair.endswith('EUR'):
                continue
            self._exchange_pairs.append(pair)

        exchange_info['pairs'] = pairs
        exchange_info['assets'] = assets

        return exchange_info

    # get list of exchange pairs (trade symbols)
    def get_exchange_pairs(self):
        if not self._exchange_pairs:
            self.load_exchange_info()

        return sorted(self._exchange_pairs)

    # is a valid exchange pair
    def is_exchange_pair(self, symbol):
        if not self._exchange_pairs:
            self.load_exchange_info()
        if symbol in self._exchange_pairs:
            return True
        return False

    def get_asset_status(self, name=None):
        result = None
        if not self.info_all_assets:
            self.load_exchange_info()
        try:
            result = self.info_all_assets[name]
        except KeyError:
            pass
        return result

    def is_asset_available(self, name):
        raise NotImplementedError

    # return asset info in AssetInfo class object
    def get_asset_info(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return None

        min_qty=float(info['min_qty'])
        min_price=float(info['min_price'])
        base_step_size=float(info['base_step_size'])
        base_precision = float(info['base_precision'])
        currency_step_size=float(info['currency_step_size'])
        currency_precision = float(info['currency_precision'])
        is_currency_pair = self.is_currency_pair(symbol=symbol, base=base, currency=currency)

        orderTypes = []

        result = AssetInfo(base=base,
                           currency=currency,
                           min_qty=min_qty,
                           min_price=min_price,
                           base_step_size=base_step_size,
                           currency_step_size=currency_step_size,
                           is_currency_pair=is_currency_pair,
                           base_precision=base_precision,
                           currency_precision=currency_precision,
                           orderTypes=orderTypes
                           )
        return result

    def get_asset_info_dict(self, symbol=None, base=None, currency=None, field=None):
        if not self.info_all_pairs:
            self.load_exchange_info()

        if not symbol:
            symbol = self.make_ticker_id(base, currency)

        if not self.info_all_pairs or symbol not in self.info_all_pairs.keys():
            self.logger.warning("symbol {} not found in assets".format(symbol))
            return None
        if field:
            if field not in self.info_all_pairs[symbol]:
                self.logger.warning("field {} not found in assets for symbol {}".format(field, symbol))
                return None
            return self.info_all_pairs[symbol][field]
        return self.info_all_pairs[symbol]
