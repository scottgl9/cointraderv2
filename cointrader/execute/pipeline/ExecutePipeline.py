# This file contains the ExecutePipeline class, which is responsible for managing the pipeline of orders to be executed, and retrieving the results of those orders.
from collections import deque
from queue import Queue
from threading import Lock
from cointrader.execute.ExecuteBase import ExecuteBase
from cointrader.order.Order import Order
from cointrader.order.OrderResult import OrderResult
from cointrader.order.OrderRequest import OrderRequest

class ExecutePipeline(object):
    _placed_orders_requests: Queue[OrderRequest]
    _processed_orders_results: dict[str, OrderResult]
    def __init__(self, execute: ExecuteBase, max_orders: int = 100):
        self._execute = execute
        self._max_orders = max_orders
        self._placed_orders_requests = Queue(maxsize=max_orders)
        self._processed_orders_results = {}
        self._lock = Lock()

    def add_order_request(self, order_request: OrderRequest):
        """
        Add order to the placed orders pipeline
        """
        self._placed_orders_requests.put(order_request)

    def get_order_result(self, request_id: str) -> OrderResult:
        """
        Get processed order by request id
        """
        result = None
        with self._lock:
            result = self._processed_orders_results.get(request_id)
        return result

    def completed(self, request_id: str) -> bool:
        """
        Indicate that the order result has been completed, so remove from processed order results
        """
        if request_id not in self._processed_orders_results:
            return False
        with self._lock:
            del self._processed_orders_results[request_id]
        return True

    def process_order_requests(self) -> int:
        """
        Process all placed orders, and move to processed orders. Returns number of orders processed
        """
        count = 0

        while not self._placed_orders_requests.empty():
            order_request = self._placed_orders_requests.get()
            result = self._execute.execute_order(order=order_request)
            # provide results in processed orders
            with self._lock:
                self._processed_orders_results[order_request.rid] = result
            count += 1

        return count
