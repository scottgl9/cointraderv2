# Base class for executing trades
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from cointrader.order.OrderResult import OrderResult
from cointrader.account.AccountBase import AccountBase

class ExecuteBase(object):
    _exchange = None
    _config = None

    def __init__(self, exchange: TraderExchangeBase):
        self._exchange = exchange

    def account(self) -> AccountBase:
        raise NotImplementedError

    def market_buy(self, symbol: str, price: float, amount: float) -> OrderResult:
        raise NotImplementedError
    
    def market_sell(self, symbol: str, price: float, amount: float) -> OrderResult:
        raise NotImplementedError
    
    def limit_buy(self, symbol: str, price: float, amount: float) -> OrderResult:
        raise NotImplementedError
    
    def limit_sell(self, symbol: str, price: float, amount: float) -> OrderResult:
        raise NotImplementedError
    
    def stop_loss_buy(self, symbol: str, price: float, stop_price: float, amount: float) -> OrderResult:
        raise NotImplementedError
    
    def stop_loss_sell(self, symbol: str, price: float, stop_price: float, amount: float) -> OrderResult:
        raise NotImplementedError
    
    def status(self, symbol: str, order_id: str, price: float) -> OrderResult:
        """
        Get order status
        """
        raise NotImplementedError
    
    def cancel(self, symbol: str, order_id: str, price: float) -> OrderResult:
        """
        Cancel an order
        """
        raise NotImplementedError
