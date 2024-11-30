# Orders class to store all orders
from .Order import Order

class Orders:
    def __init__(self):
        self.orders = {}

    def add_order(self, symbol: str, order: Order):
        if symbol not in self.orders:
            self.orders[symbol] = { order.order_id: order }
        else:
            self.orders[symbol][order.order_id] = order

    def get_order(self, symbol: str, order_id: str) -> Order:
        if symbol in self.orders and order_id in self.orders[symbol]:
            return self.orders[symbol][order_id]
        return None

    def remove_order(self, symbol: str, order_id: str) -> bool:
        if symbol in self.orders and order_id in self.orders[symbol]:
            del self.orders[symbol][order_id]
            return True
        return False
