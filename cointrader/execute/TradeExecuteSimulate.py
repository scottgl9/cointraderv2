# Implement simulate trading execution for backtesting
from cointrader.client.TraderClientBase import TraderClientBase
from .ExecuteBase import ExecuteBase
from cointrader.order.OrderResult import OrderResult
from cointrader.order.Order import OrderStatus, OrderType, OrderSide
import uuid

class TraderExecuteSimulate(ExecuteBase):
    def __init__(self, client: TraderClientBase):
        self._client = client
    
    def market_buy(self, symbol: str, price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.FILLED
        result.side = OrderSide.BUY
        result.type = OrderType.MARKET
        result.price = price
        result.size = amount
        result.filled_size = amount
        return result
    
    def market_sell(self, symbol: str, price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.FILLED
        result.side = OrderSide.SELL
        result.type = OrderType.MARKET
        result.price = price
        result.size = amount
        result.filled_size = amount
        return result
    
    def limit_buy(self, symbol: str, price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.BUY
        result.type = OrderType.LIMIT
        result.price = price
        result.size = amount
        result.filled_size = 0.0
        return result

    def limit_sell(self, symbol: str, price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.SELL
        result.type = OrderType.LIMIT
        result.price = price
        result.size = amount
        result.filled_size = 0.0
        return result

    def stop_loss_buy(self, symbol: str, price: float, stop_price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.BUY
        result.type = OrderType.STOP_LOSS_LIMIT
        result.price = price
        result.limit_price = stop_price
        result.size = amount
        result.filled_size = 0.0
        return result
    
    def stop_loss_sell(self, symbol: str, price: float, stop_price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.SELL
        result.type = OrderType.STOP_LOSS_LIMIT
        result.price = price
        result.limit_price = stop_price
        result.size = amount
        result.filled_size = 0.0
        return result
