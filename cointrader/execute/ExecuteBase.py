# Base class for executing trades
from cointrader.client.TraderClientBase import TraderClientBase

class ExecuteBase(object):
    _client = None
    def __init__(self, client: TraderClientBase):
        self._client = client

    def market_buy(self, symbol: str, price: float, amount: float):
        raise NotImplementedError
    
    def market_sell(self, symbol: str, price: float, amount: float):
        raise NotImplementedError
    
    def limit_buy(self, symbol: str, price: float, amount: float):
        raise NotImplementedError
    
    def limit_sell(self, symbol: str, price: float, amount: float):
        raise NotImplementedError
    
    def stop_loss_buy(self, symbol: str, price: float, stop_price: float, amount: float):
        raise NotImplementedError
    
    def stop_loss_sell(self, symbol: str, price: float, stop_price: float, amount: float):
        raise NotImplementedError
