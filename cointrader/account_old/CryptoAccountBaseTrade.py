# base account class for handling account executed trades

class CryptoAccountBaseTrade(object):
    def buy_market(self, size, price=0.0, ticker_id=None):
        raise NotImplementedError

    def sell_market(self, size, price=0.0, ticker_id=None):
        raise NotImplementedError

    def buy_limit(self, price, size, ticker_id=None):
        raise NotImplementedError

    def sell_limit(self, price, size, ticker_id=None):
        raise NotImplementedError

    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        raise NotImplementedError

    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):
        raise NotImplementedError

    def get_order(self, order_id, ticker_id):
        raise NotImplementedError

    def get_orders(self, ticker_id=None):
        raise NotImplementedError

    def cancel_order(self, orderid, ticker_id=None):
        raise NotImplementedError

    def parse_order_update(self, result):
        raise NotImplementedError

    # parse json response to order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        raise NotImplementedError
