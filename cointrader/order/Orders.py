# Orders class to store all orders
from .Order import Order
from .OrderStorage import OrderStorage

class Orders:
    def __init__(self, order_storage: OrderStorage = None, db_path='orders.db', reset=True):
        self.orders = {}
        self._db_path = db_path
        if db_path is None:
            self._order_storage = None
        elif order_storage is not None:
            self._order_storage = order_storage
        else:
            self._order_storage = OrderStorage(db_path=db_path, reset=reset)

    def add_order(self, symbol: str, order: Order):
        if symbol not in self.orders:
            self.orders[symbol] = { order.id: order }
        else:
            self.orders[symbol][order.id] = order
        
        if self._order_storage:
            self._order_storage.add_order(order)
        elif symbol not in self.orders:
            self.orders[symbol] = { order.id: order }
        else:
            self.orders[symbol][order.id] = order

    def get_order(self, symbol: str, order_id: str) -> Order:
        if self._order_storage:
            return self._order_storage.get_order(order_id=order_id)
        elif symbol in self.orders and order_id in self.orders[symbol]:
            return self.orders[symbol][order_id]
        
        return None

    def get_all_orders(self, symbol: str) -> list:
        """
        Get all orders for a symbol
        """
        if self._order_storage:
            return self._order_storage.get_all_orders()
        elif symbol in self.orders:
            return list(self.orders[symbol].values())

    def get_active_orders(self, symbol: str) -> list:
        """
        Get all active orders for a symbol
        """
        if self._order_storage:
            return self._order_storage.get_active_orders()
        elif symbol in self.orders:
            return [order for order in self.orders[symbol].values() if order.active]

    def update_order(self, symbol: str, order: Order):
        if self._order_storage:
            self._order_storage.update_order(order)
        elif symbol in self.orders and order.id in self.orders[symbol]:
            self.orders[symbol][order.id] = order

    def update_order_active(self, symbol: str, order_id: str, active: bool):
        if self._order_storage:
            self._order_storage.update_order_active(order_id=order_id, active=active)
        elif symbol in self.orders and order_id in self.orders[symbol]:
            self.orders[symbol][order_id].active = active

    def remove_order(self, symbol: str, order_id: str) -> bool:
        if symbol in self.orders and order_id in self.orders[symbol]:
            del self.orders[symbol][order_id]
            return True
        return False

    def commit(self):
        if self._order_storage:
            self._order_storage.commit()
