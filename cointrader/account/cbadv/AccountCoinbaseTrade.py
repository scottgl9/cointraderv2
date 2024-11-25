from trader.account.CryptoAccountBaseTrade import CryptoAccountBaseTrade
from trader.lib.struct.TraderMessage import TraderMessage
from trader.lib.struct.Order import Order
from trader.lib.struct.OrderUpdate import OrderUpdate
from coinbase.rest import RESTClient


class AccountCoinbaseTrade(CryptoAccountBaseTrade):
    def __init__(self, client : RESTClient, info, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulate
        self.logger = logger

    def buy_market(self, size, price=0.0, ticker_id=None):
        return self.client.market_order_buy(client_order_id='', product_id=ticker_id, base_size=size)

    def sell_market(self, size, price=0.0, ticker_id=None):
       return self.client.market_order_sell(client_order_id='', product_id=ticker_id, base_size=size)

    def buy_limit(self, price, size, ticker_id=None):
        # use GTC so that order doesn't expire
        return self.client.limit_order_gtc_buy(client_order_id='', product_id=ticker_id, limit_price=price, base_size=size)

    def sell_limit(self, price, size, ticker_id=None):
        # use GTC so that order doesn't expire
        return self.client.limit_order_gtc_sell(client_order_id='', product_id=ticker_id, limit_price=price, base_size=size)

    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        # use GTC so that order doesn't expire
        return self.client.stop_limit_order_gtc_buy(client_order_id='', product_id=ticker_id, limit_price=price, stop_price=stop_price, base_size=size)

    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):
        # use GTC so that order doesn't expire
        return self.client.stop_limit_order_gtc_sell(client_order_id='', product_id=ticker_id, limit_price=price, stop_price=stop_price, base_size=size)

    def get_order(self, order_id, ticker_id):
        return self.client.get_order(order_id=order_id)

    def get_orders(self, ticker_id=None):
        raise NotImplementedError

    def cancel_order(self, orderid, ticker_id=None):
        return self.client.cancel_orders(order_ids=[orderid])

    def parse_order_update(self, result):
        raise NotImplementedError

    # parse json response to order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        raise NotImplementedError
