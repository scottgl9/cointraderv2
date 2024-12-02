# Base class for executing trades
from cointrader.client.TraderClientBase import TraderClientBase
from cointrader.order.OrderResult import OrderResult

class ExecuteBase(object):
    _client = None
    def __init__(self, client: TraderClientBase):
        self._client = client

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
