# Base class for executing trades
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from cointrader.order.OrderResult import OrderResult
from decimal import Decimal

class ExecuteBase(object):
    _exchange = None
    def __init__(self, exchange: TraderExchangeBase):
        self._exchange = exchange

    def market_buy(self, symbol: str, price: Decimal, amount: Decimal) -> OrderResult:
        raise NotImplementedError
    
    def market_sell(self, symbol: str, price: Decimal, amount: Decimal) -> OrderResult:
        raise NotImplementedError
    
    def limit_buy(self, symbol: str, price: Decimal, amount: Decimal) -> OrderResult:
        raise NotImplementedError
    
    def limit_sell(self, symbol: str, price: Decimal, amount: Decimal) -> OrderResult:
        raise NotImplementedError
    
    def stop_loss_buy(self, symbol: str, price: Decimal, stop_price: Decimal, amount: Decimal) -> OrderResult:
        raise NotImplementedError
    
    def stop_loss_sell(self, symbol: str, price: Decimal, stop_price: Decimal, amount: Decimal) -> OrderResult:
        raise NotImplementedError
    
    def status(self, symbol: str, order_id: str, price: Decimal) -> OrderResult:
        """
        Get order status
        """
        raise NotImplementedError
    
    def cancel(self, symbol: str, order_id: str, price: Decimal) -> OrderResult:
        """
        Cancel an order
        """
        raise NotImplementedError
