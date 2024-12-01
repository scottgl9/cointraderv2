# This file contains the OrderResult class which is used to store the result of an order request.
from .Order import OrderStatus, OrderType, OrderSide

class OrderResult(object):
    def __init__(self, symbol: str):
        self.id = ""
        self.symbol = symbol
        self.type = OrderType.UNKNOWN
        self.side = OrderSide.UNKNOWN
        self.price = 0.0
        self.limit_price = 0.0
        self.size = 0.0
        self.filled_size = 0.0
        self.timestamp = 0
        self.msg = ""
        self.status = OrderStatus.UNKNOWN
        self.error_msg = ""

    def from_dict(self, data: dict):
        self.id = data['id']
        self.symbol = data['symbol']
        self.type = data['type']
        self.side = data['side']
        self.price = data['price']
        self.limit_price = data['limit_price']
        self.size = data['size']
        self.filled_size = data['filled_size']
        self.timestamp = data['timestamp']
        self.msg = data['msg']
        self.status = data['status']
        self.error_msg = data['error_msg']

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'type': self.type,
            'side': self.side,
            'price': self.price,
            'limit_price': self.limit_price,
            'size': self.size,
            'filled_size': self.filled_size,
            'timestamp': self.timestamp,
            'msg': self.msg,
            'status': self.status,
            'error_msg': self.error_msg
        }

    def __dict__(self):
        return self.to_dict()

    def __repr__(self) -> dict:
        return self.to_dict()