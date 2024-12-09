# Orders class to store all orders
from .Order import Order
from .OrderStorage import OrderStorage

class Orders:
    def __init__(self, order_storage: OrderStorage = None, db_path='orders.db'):
        self.orders = {}
        self._db_path = db_path
        if not order_storage:
            self._order_storage = OrderStorage(db_path)
        else:
            self._order_storage = order_storage

    def add_order(self, symbol: str, order: Order):
        if symbol not in self.orders:
            self.orders[symbol] = { order.id: order }
        else:
            self.orders[symbol][order.id] = order
        self._order_storage.add_order(order)

    def get_order(self, symbol: str, order_id: str) -> Order:
        if symbol in self.orders and order_id in self.orders[symbol]:
            return self.orders[symbol][order_id]
        return None

    def remove_order(self, symbol: str, order_id: str) -> bool:
        if symbol in self.orders and order_id in self.orders[symbol]:
            del self.orders[symbol][order_id]
            return True
        return False
