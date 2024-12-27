# This file contains the OrderResult class which is used to store the result of an order request.
import json
from .enum.OrderType import OrderType
from .enum.OrderSide import OrderSide
from .enum.OrderStatus import OrderStatus
from .enum.OrderLimitType import OrderLimitType
from .enum.OrderStopDirection import OrderStopDirection
from .enum.OrderErrorReason import OrderErrorReason

class OrderResult(object):
    id: str                             # Order ID
    pid: int                            # Position ID (used for restoring positions)
    active: bool                        # Active order
    symbol: str                         # Symbol (e.g. BTC/USD)
    type: OrderType                     # Order type (e.g. MARKET, LIMIT)
    limit_type: OrderLimitType          # Limit type (e.g. GTC, IOC)
    side: OrderSide                     # Order side (e.g. BUY, SELL)
    price: float                        # Executed order price
    limit_price: float                  # Limit price
    stop_price: float                   # Stop price
    stop_direction: OrderStopDirection  # Stop direction (e.g. ABOVE, BELOW)
    size: float                         # Order size
    filled_size: float                  # Filled order size
    fee: float                          # Order fee
    placed_ts: int                      # Order placed timestamp
    filled_ts: int                      # Order filled timestamp
    msg: str                            # Raw result message
    post_only: bool                     # Post only order
    status: OrderStatus                 # Order status
    error_reason: OrderErrorReason      # Order error reason
    error_msg: str                      # Error message

    def __init__(self, symbol: str):
        self.id = ""
        self.pid: int = 0
        self.active = True
        self.symbol = symbol
        self.type = OrderType.UNKNOWN
        self.limit_type = OrderLimitType.UNKNOWN
        self.side = OrderSide.UNKNOWN
        self.price = 0.0
        self.limit_price = 0.0
        self.stop_price = 0.0
        self.stop_direction = OrderStopDirection.UNKNOWN
        self.size = 0.0
        self.filled_size = 0.0
        self.fee = 0.0
        self.placed_ts = 0
        self.filled_ts = 0
        self.msg = ""
        self.post_only = False
        self.status = OrderStatus.UNKNOWN
        self.error_reason = OrderErrorReason.NONE
        self.error_msg = ""

    def from_dict(self, data: dict):
        self.id = data['id']
        if 'pid' in data:
            self.id = data['pid']
        if 'active' in data:
            self.active = data['active']
        if 'symbol' in data:
            self.symbol = data['symbol']
        self.type = OrderType(data['type'])
        self.limit_type = OrderLimitType(data['limit_type'])
        self.side = OrderSide(data['side'])
        self.price = data['price']
        self.limit_price = data['limit_price']
        self.stop_price = data['stop_price']
        self.stop_direction = OrderStopDirection(data['stop_direction'])
        self.size = data['size']
        self.filled_size = data['filled_size']
        self.fee = data['fee']
        self.placed_ts = data['placed_ts']
        self.filled_ts = data['filled_ts']
        self.msg = data['msg']
        self.post_only = data['post_only']
        self.status = OrderStatus(data['status'])
        self.error_reason = OrderErrorReason(data['error_reason'])
        self.error_msg = data['error_msg']

    def to_dict(self):
        return {
            'id': self.id,
            'pid': self.pid,
            'active': self.active,
            'symbol': self.symbol,
            'type': self.type.name,
            'limit_type': self.limit_type.name,
            'side': self.side.name,
            'price': self.price,
            'limit_price': self.limit_price,
            'stop_price': self.stop_price,
            'stop_direction': self.stop_direction.name,
            'size': self.size,
            'filled_size': self.filled_size,
            'fee': self.fee,
            'placed_ts': self.placed_ts,
            'filled_ts': self.filled_ts,
            'msg': self.msg,
            'post_only': self.post_only,
            'status': self.status.name,
            'error_reason': self.error_reason.name,
            'error_msg': self.error_msg
        }

    def __dict__(self):
        return self.to_dict()

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return json.dumps(self.to_dict())
