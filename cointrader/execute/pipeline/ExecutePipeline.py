# This file contains the ExecutePipeline class, which is responsible for managing the pipeline of orders to be executed, and retrieving the results of those orders.
from collections import deque
from queue import Queue
from threading import Lock
from cointrader.execute.ExecuteBase import ExecuteBase
from cointrader.order.Order import Order
from cointrader.order.OrderResult import OrderResult

class ExecutePipeline(object):
    _placed_orders: Queue[Order]
    _processed_orders: dict[str, Order]
    def __init__(self, execute: ExecuteBase, max_orders: int = 100):
        self._execute = execute
        self._max_orders = max_orders
        self._placed_orders = Queue(maxsize=max_orders)
        self._processed_orders = {}
        self._lock = Lock()

    def add_order(self, order: Order) -> OrderResult:
        """
        Add order to the placed orders pipeline
        """
        self._placed_orders.put(order)

    def get_order(self, order_id: str) -> Order:
        """
        Get processed order by order id
        """
        result = None
        with self._lock:
            result = self._processed_orders.get(order_id)
        return result

    def completed(self, order_id: str) -> bool:
        """
        Indicate that the order has been completed, so remove from processed orders
        """
        if order_id not in self._processed_orders:
            return False
        with self._lock:
            del self._processed_orders[order_id]
        return True

    def process_orders(self) -> int:
        """
        Process all placed orders, and move to processed orders. Returns number of orders processed
        """
        count = 0

        while not self._placed_orders.empty():
            order = self._placed_orders.get()
            result = self._execute.execute_order(order=order)
            order.update_order(result)
            # moved order from placed to processed orders
            with self._lock:
                self._processed_orders[order.id] = order
            count += 1

        return count
