from cointrader.exchange.cbadv.CBADVTraderExchange import CBADVTraderExchange
from cointrader.config import CBADV_KEY, CBADV_SECRET
class TraderSelectExchange:
    def __init__(self, exchange_name):
        self.exchange = self.select_exchange(exchange_name)

    def get_exchange(self):
        return self.exchange

    def select_exchange(self, exchange_name):
        exchanges = {
            "cbadv": (CBADVTraderExchange, CBADV_KEY, CBADV_SECRET),
        }
        if exchange_name.lower() not in exchanges:
            raise ValueError(f"Unknown exchange: {exchange_name}")
        exchange, key, secret = exchanges[exchange_name.lower()]
        return exchange(key, secret)
