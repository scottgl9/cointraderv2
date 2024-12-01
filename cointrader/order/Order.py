# Description: Order class for representing an order
from enum import Enum
from .OrderResult import OrderResult

class OrderStatus(Enum):
    UNKNOWN = 0
    NEW = 1
    PLACED = 2
    PARTIALLY_FILLED = 3
    FILLED = 4
    CANCELED = 5
    PENDING_CANCEL = 6
    REJECTED = 7
    EXPIRED = 8

class OrderType(Enum):
    UNKNOWN = 0
    LIMIT = 1
    MARKET = 2
    STOP_LOSS = 3
    TAKE_PROFIT = 4

class OrderSide(Enum):
    UNKNOWN = 0
    BUY = 1
    SELL = 2

class Order(object):
    def __init__(self, symbol: str, order_id: str, type: OrderType, side: OrderSide, price: float, limit_price: float, size: float, timestamp: int):
        self._last_order_result = None
        self.symbol = symbol
        self.order_id = order_id
        self.status = OrderStatus.NEW
        self.order_type = type
        self.order_side = side
        self.size = size
        self.filled_size = 0.0
        self.price = price
        self.limit_price = limit_price
        self.timestamp = timestamp

    def update_order_result(self, result: OrderResult):
        self._last_order_result = result
        self.status = result.status
        self.filled_size = result.filled_size
        self.timestamp = result.timestamp

    def from_dict(self, data: dict):
        self.symbol = data['symbol']
        self.order_id = data['order_id']
        self.status = data['status']
        self.order_type = data['type']
        self.order_side = data['side']
        self.size = data['size']
        self.filled_size = data['filled_size']
        self.price = data['price']
        self.limit_price = data['limit_price']
        self.timestamp = data['timestamp']

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'order_id': self.order_id,
            'status': self.status,
            'order_type': self.order_type,
            'order_side': self.order_side,
            'size': self.size,
            'filled_size': self.filled_size,
            'price': self.price,
            'limit_price': self.limit_price,
            'timestamp': self.timestamp
        }

    def __dict__(self):
        return self.to_dict()

    def __repr__(self) -> dict:
        return self.to_dict()
