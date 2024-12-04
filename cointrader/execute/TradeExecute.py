from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from cointrader.order.OrderResult import OrderResult
from cointrader.account.AccountBase import AccountBase
from .ExecuteBase import ExecuteBase
from decimal import Decimal

class TraderExecute(ExecuteBase):
    def __init__(self, exchange: TraderExchangeBase, account: AccountBase):
        self._exchange = exchange
    
    def market_buy(self, symbol: str, price: Decimal, amount: Decimal) -> OrderResult:
        return self._exchange.trade_buy_market(symbol, amount)
    
    def market_sell(self, symbol: str, price: Decimal, amount: Decimal) -> OrderResult:
        return self._exchange.trade_sell_market(symbol, amount)
    
    def limit_buy(self, symbol: str, price: Decimal, amount: Decimal) -> OrderResult:
        return self._exchange.trade_buy_limit(symbol, price, amount)
    
    def limit_sell(self, symbol: str, price: Decimal, amount: Decimal) -> OrderResult:
        return self._exchange.trade_sell_limit(symbol, price, amount)
    
    def stop_loss_buy(self, symbol: str, price: Decimal, stop_price: Decimal, amount: Decimal) -> OrderResult:
        return self._exchange.trade_buy_stop_limit(symbol, price, stop_price, amount)
    
    def stop_loss_sell(self, symbol: str, price: Decimal, stop_price: Decimal, amount: Decimal) -> OrderResult:
        return self._exchange.trade_sell_stop_limit(symbol, price, stop_price, amount)

    def status(self, symbol: str, order_id: str, price: Decimal = 0) -> OrderResult:
        return self._exchange.trade_get_order(symbol, order_id)

    def cancel(self, symbol: str, order_id: str, price: Decimal = 0) -> OrderResult:
        return self._exchange.trade_cancel_order(symbol, order_id)
