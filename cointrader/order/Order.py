# Description: Order class for representing an order
from enum import Enum
from .OrderResult import OrderResult
from .enum.OrderSide import OrderSide
from .enum.OrderType import OrderType
from .enum.OrderLimitType import OrderLimitType
from .enum.OrderStopDirection import OrderStopDirection
from .enum.OrderStatus import OrderStatus

class Order(OrderResult):
    def __init__(self, symbol: str, data: dict = None):
        super().__init__(symbol)
        self.symbol = symbol
        self._last_order_result = None
        if data:
            self.from_dict(data)

    def update_order(self, result: OrderResult):
        """
        Update the order with the result of the last order status
        """
        self._last_order_result = result
        if not self.id:
            self.id = result.id
        if not self.symbol:
            self.symbol = result.symbol
        if self.type == OrderType.UNKNOWN:
            self.type = result.type
        if self.limit_type == OrderLimitType.UNKNOWN:
            self.limit_type = result.limit_type
        if self.side == OrderSide.UNKNOWN:
            self.side = result.side
        if self.price == 0.0 or (result.price != 0.0 and self.price != result.price):
            self.price = result.price
        if self.limit_price == 0.0:
            self.limit_price = result.limit_price
        if self.stop_price == 0.0:
            self.stop_price = result.stop_price
        if self.stop_direction == OrderStopDirection.UNKNOWN:
            self.stop_direction = result.stop_direction
        if self.size == 0.0:
            self.size = result.size
        if self.filled_size == 0.0 or (result.filled_size != 0.0 and self.filled_size != result.filled_size):
            self.filled_size = result.filled_size
        if self.fee == 0.0:
            self.fee = result.fee
        if self.placed_ts == 0:
            self.placed_ts = result.placed_ts
        if self.filled_ts == 0:
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

    def cancelled(self) -> bool:
        """
        Check if the order has been cancelled
        """
        return self.status == OrderStatus.CANCELLED
