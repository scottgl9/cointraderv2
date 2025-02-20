from .Order import Order
from .enum.OrderType import OrderType
from .enum.OrderSide import OrderSide
import uuid

class OrderRequest(object):
    current_price: float                # Current price (used for simulation only)
    current_ts: int                     # Current timestamp (used for simulation only)

    def __init__(self, symbol: str, type: OrderType = OrderType.UNKNOWN, side: OrderSide = OrderSide.NONE, size=0.0, current_price=0.0, current_ts=0):
        self.symbol = symbol
        self.type = type
        self.side = side
        self.current_price = current_price
        self.current_ts = current_ts
        # Order ID
        self.order_id = None
        # Request ID
        self.rid = str(uuid.uuid4())
        self.limit_price = 0.0
        self.stop_price = 0.0
        self.size = size
