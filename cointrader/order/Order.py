# Description: Order class for representing an order

class OrderStatus:
    NEW = 0
    PARTIALLY_FILLED = 1
    FILLED = 2
    CANCELED = 3
    PENDING_CANCEL = 4
    REJECTED = 5
    EXPIRED = 6

class OrderType:
    LIMIT = 0
    MARKET = 1
    STOP_LOSS = 2
    TAKE_PROFIT = 3

    @staticmethod
    def name(value):
        if value == OrderType.LIMIT:
            return 'LIMIT'
        elif value == OrderType.MARKET:
            return 'MARKET'
        elif value == OrderType.STOP_LOSS:
            return 'STOP_LOSS'
        elif value == OrderType.TAKE_PROFIT:
            return 'TAKE_PROFIT'
        else:
            return 'UNKNOWN'

class OrderSide:
    BUY = 0
    SELL = 1

    @staticmethod
    def name(value):
        if value == OrderSide.BUY:
            return 'BUY'
        elif value == OrderSide.SELL:
            return 'SELL'
        else:
            return 'UNKNOWN'

class Order(object):
    def __init__(self, symbol: str, order_id: str, order_type: OrderType, order_side: OrderSide, price: float, timestamp: int, quantity: float):
        self.symbol = symbol
        self.order_id = order_id
        self.status = OrderStatus.NEW
        self.order_type = order_type
        self.order_side = order_side
        self.quantity = quantity
        self.filled_quantity = 0
        self.remaining_quantity = 0
        self.price = price
        self.timestamp = timestamp

    def from_dict(self, data: dict):
        self.symbol = data['symbol']
        self.order_id = data['order_id']
        self.status = data['status']
        self.order_type = data['order_type']
        self.order_side = data['order_side']
        self.base_size = data['base_size']
        self.quote_size = data['quote_size']
        self.filled_quantity = data['filled_quantity']
        self.remaining_quantity = data['remaining_quantity']
        self.price = data['price']
        self.timestamp = data['timestamp']

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'order_id': self.order_id,
            'status': self.status,
            'order_type': self.order_type,
            'order_side': self.order_side,
            'quantity': self.quantity,
            'filled_quantity': self.filled_quantity,
            'remaining_quantity': self.remaining_quantity,
            'price': self.price,
            'timestamp': self.timestamp
        }

    def __dict__(self):
        return self.to_dict()

    def __repr__(self) -> dict:
        return self.to_dict()
    