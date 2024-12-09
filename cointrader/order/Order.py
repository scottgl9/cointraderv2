# Description: Order class for representing an order
from enum import Enum
from .OrderResult import OrderResult
from .OrderSide import OrderSide
from .OrderType import OrderType
from .OrderStatus import OrderStatus

class Order(OrderResult):
    def __init__(self, symbol: str):
        self.symbol = symbol
        self._last_order_result = None

    def update_order(self, result: OrderResult):
        """
        Update the order with the result of the last order status
        """
        self._last_order_result = result
        self.id = result.id
        self.symbol = result.symbol
        self.type = result.type
        self.limit_type = result.limit_type
        self.side = result.side
        self.price = result.price
        self.limit_price = result.limit_price
        self.stop_price = result.stop_price
        self.stop_direction = result.stop_direction
        self.size = result.size
        self.filled_size = result.filled_size
        self.fee = result.fee
        self.placed_ts = result.placed_ts
        self.filled_ts = result.filled_ts
        self.msg = result.msg
        self.post_only = result.post_only
        self.status = result.status
        self.error_reason = result.error_reason
        self.error_msg = result.error_msg

    def completed(self) -> bool:
        """
        Check if the order has been completed
        """
        return self.filled_size == self.size and self.status == OrderStatus.FILLED
