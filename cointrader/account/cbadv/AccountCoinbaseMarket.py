from trader.account.CryptoAccountBaseMarket import CryptoAccountBaseMarket
from coinbase.rest import RESTClient
from datetime import datetime, timedelta
import time
import aniso8601
import stix.utils.dates

class AccountCoinbaseMarket(CryptoAccountBaseMarket):
    def __init__(self, client: RESTClient, info, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulate
        self.logger = logger
        self._tickers = {}
        self._min_tickers = {}
        self._max_tickers = {}
        self.granularity_mapping = {
            60: 'ONE_MINUTE',
            300: 'FIVE_MINUTE',
            900: 'FIFTEEN_MINUTE',
            3600: 'ONE_HOUR',
            21600: 'SIX_HOUR',
            86400: 'ONE_DAY',
        }

    def ts_to_iso8601(self, ts):
        dt = datetime.fromtimestamp(ts)
        return stix.utils.dates.serialize_value(dt)

    def get_all_tickers(self):
        result = {}
        if not self.simulate:
            products = self.client.get_products().products
            for product in products:
                result[product.product_id] = product.price
        else:
            return self._tickers
        return result

    def get_ticker(self, symbol=None):
        if not self.simulate:
            pairs = self.info.get_exchange_pairs()
            if symbol in pairs:
                price = self.client.get_product(symbol).price
                return price
            else:
                return 0.0
            # print(products.products)
            # if symbol in products:
            #     result = products.products[symbol]
            #     print(result)
            #     if result:
            #         price = float(result.price)
            #         return price
            #     else:
            #         return 0.0

            #elif not len(self._tickers):
            #    self._tickers = self.get_all_tickers()
        try:
            price = self._tickers[symbol]
        except KeyError:
            price = 0.0
        return price

    def get_tickers(self):
        return self._tickers

    def get_ticker_symbols(self, currency=None):
        result = []
        if not self.simulate:
            products = self.pc.get_products()
            for product in products:
                if currency and product['id'].endswith(currency):
                    result.append(product['id'])
                else:
                    result.append(product['id'])
        else:
            result = self.info.get_info_all_pairs().keys()
        return result

    def get_min_tickers(self):
        return self._min_tickers

    def get_max_tickers(self):
        return self._max_tickers

    def update_ticker(self, symbol, price, ts):
        if self.simulate:
            last_price = 0
            try:
                last_price = self._tickers[symbol]
            except KeyError:
                pass

            if not last_price:
                self._min_tickers[symbol] = [price, ts]
                self._max_tickers[symbol] = [price, ts]
            else:
                if price < self._min_tickers[symbol][0]:
                    self._min_tickers[symbol] = [price, ts]
                elif price > self._max_tickers[symbol][0]:
                    self._max_tickers[symbol] = [price, ts]

        self._tickers[symbol] = price

    def update_tickers(self, tickers):
        for symbol, price in tickers.items():
            self._tickers[symbol] = float(price)

    # The granularity field must be one of the following values: {60, 300, 900, 3600, 21600, 86400}
    # The maximum amount of data returned is 300 candles
    # kline format: [ timestamp, low, high, open, close, volume ]
    def get_klines(self, days=0, hours=1, mode=None, ticker_id=None, granularity=3600):
        end = datetime.now()
        start = int((end - timedelta(days=days, hours=hours)).timestamp())
        end = int(end.timestamp())

        candles = self.client.get_candles(ticker_id, start, end, granularity=self.granularity_mapping[granularity])
        candles = candles['candles']
        #candles = [candle.__repr__() for candle in candles]
        candles = [candle.__dict__ for candle in candles]
        return candles

    def get_hourly_klines(self, symbol, start_ts, end_ts, reverse=False):
        MAX_CANDLES = 350
        granularity = self.granularity_mapping[3600]
        result = []
        if not reverse:
            ts1 = start_ts
            ts2 = end_ts
            while ts1 <= end_ts:
                ts2 = end_ts
                if (ts2 - ts1) > 3600 * MAX_CANDLES:
                    ts2 = ts1 + 3600 * MAX_CANDLES
                start = ts1
                end = ts2

                candles = self.client.get_candles(symbol, start, end, granularity=granularity)
                candles = candles['candles']
                #candles = [candle.__repr__() for candle in candles]
                klines = [candle.__dict__ for candle in candles]
                ts1 = ts2 + 3600
                if isinstance(klines, list):
                    try:
                        if len(klines):
                            result += reversed(klines)
                    except TypeError:
                        print(klines, type(klines))
                        pass
                    time.sleep(1)
                else:
                    if klines['message'] == 'NotFound':
                        time.sleep(1)
                        continue
                    print("ERROR get_hourly_klines(): {}".format(klines['message']))
                    return result

        return result
