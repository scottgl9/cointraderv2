from cointrader.common.Strategy import Strategy
from cointrader.common.Kline import Kline
from cointrader.order.Order import Order, OrderSide, OrderType, OrderStatus
from cointrader.order.Orders import Orders
from cointrader.execute.ExecuteBase import ExecuteBase
from cointrader.trade.TraderConfig import TraderConfig
import time

class PositionBase(object):
    _symbol = None
    _config: TraderConfig = None
    _buy_order: Order = None
    _sell_order: Order = None
    _stop_loss_order: Order = None
    _last_stop_loss_order: Order = None

    def __init__(self, symbol: str, pid: int, strategy: Strategy, execute: ExecuteBase, config: TraderConfig, orders: Orders):
        self._pid = pid
        self._symbol = symbol
        self._config = config
        self._orders = orders
        self._buy_order = None
        self._sell_order = None
        self._last_stop_loss_order = None
        self._stop_loss_order = None
        self._strategy = strategy
        self._execute = execute
        self._account = execute.account()
        self._opened_position = False
        self._opened_position_completed = False
        self._closed_position = False
        self._closed_position_completed = False
        self._current_price = 0
        self._current_ts = 0


    def pid(self):
        """
        Get the position id
        """
        return self._pid


    def symbol(self):
        """
        Get the symbol for the position
        """
        return self._symbol


    def buy_order(self):
        """
        Get the buy order
        """
        return self._buy_order


    def sell_order(self):
        """
        Get the sell order
        """
        return self._sell_order


    def stop_loss_order(self):
        """
        Get the trailing stop loss order
        """
        return self._stop_loss_order


    def restore_buy_order(self, order: Order, current_price: float, current_ts: int):
        """
        Restore the buy order from the database
        """
        self._buy_order = order
        self._opened_position_completed = True
        self._current_price = current_price
        self._current_ts = current_ts


    def opened_position(self):
        return self._opened_position


    def opened_position_completed(self):
        return self._opened_position_completed


    def closed_position(self):
        return self._closed_position


    def closed_position_completed(self):
        return self._closed_position_completed


    def closed(self):
        if self.sell_order_completed():
            return True
        if self.stop_loss_is_completed():
            return True
        return False


    def opened(self):
        return not self.closed() and self.buy_order_completed()


    def stop_loss_is_set(self):
        return self._stop_loss_order is not None


    def stop_loss_price(self):
        order = self.stop_loss_order()
        if order is None:
            return 0.0
        return order.stop_price


    def stop_loss_limit_price(self):
        order = self.stop_loss_order()
        if order is None:
            return 0.0
        return order.limit_price


    def stop_loss_is_cancelled(self):
        """
        Check if the stop loss order has been cancelled
        """
        return self._stop_loss_order and self._stop_loss_order.cancelled()


    def stop_loss_is_completed(self):
        """
        Check if the stop loss order has been filled
        """
        return self._stop_loss_order and self._stop_loss_order.completed()


    def buy_order_completed(self):
        """
        Check if the buy order has been filled
        """
        return self._buy_order and self._buy_order.completed()
    

    def sell_order_completed(self):
        """
        Check if the sell order has been filled
        """
        return self._sell_order and self._sell_order.completed()


    def buy_price(self):
        if not self.buy_order_completed():
            return 0.0
        return self._buy_order.price


    def buy_size(self):
        if not self.buy_order_completed():
            return 0.0
        return self._buy_order.filled_size    


    def buy_ts(self):
        if not self.buy_order_completed():
            return 0
        return self._buy_order.filled_ts


    def sell_ts(self):
        if not self.sell_order_completed():
            if not self.stop_loss_is_completed():
                return 0
            else:
                return self._stop_loss_order.filled_ts
        return self._sell_order.filled_ts


    def sell_price(self):
        if not self.sell_order_completed():
            if not self.stop_loss_is_completed():
                return 0.0
            else:
                return self._stop_loss_order.price
        return self._sell_order.price


    def buy_info(self):
        return {'price': self.buy_price(), 'ts': self.buy_ts()}


    def sell_info(self):
        return {'price': self.sell_price(), 'ts': self.sell_ts()}


    def get_buy_position(self) -> Order:
        """
        Get the buy order information
        """
        if not self.opened():
            return None

        return self._buy_order


    def create_stop_loss_position(self, stop_price: float, limit_price: float, current_ts: int):
        """
        Create a stop loss order
        """
        raise NotImplementedError


    def update_stop_loss_position(self) -> Order:
        """
        Get the stop loss order information from exchange (real or simulated)
        """
        raise NotImplementedError


    def cancel_stop_loss_position(self):
        """
        Cancel the stop loss order
        """
        raise NotImplementedError


    def open_position(self, size: float, current_price: float, current_ts: int):
        """
        Open a position with a buy order
        """
        raise NotImplementedError


    def update_buy_position(self, size: float, current_price: float, current_ts: int):
        """
        For limit and stop loss limit orders, check if the buy order should be cancelled and replaced
        """
        raise NotImplementedError


    def update_sell_position(self, current_price: float, current_ts: int):
        """
        For limit and stop loss limit orders, check if the sell order should be cancelled and replaced
        """
        raise NotImplementedError


    def close_position(self, current_price: float, current_ts: int):
        """
        Close the position with a sell order
        """
        raise NotImplementedError


    def market_update(self, current_price: float, current_ts: int):
        """
        Update the position with order status and the current market price
        """
        raise NotImplementedError


    def current_position_percent(self, price: float):
        """
        Calculate the current position percent for an open position
        """
        if not self.buy_order_completed():
            return 0.0
        buy_price = self.buy_price()
        if buy_price == 0.0:
            return 0.0
        return (price - buy_price) / buy_price * 100


    def profit_percent(self):
        """
        Calculate the profit percent for a closed position
        """
        profit = 0.0

        if not self.buy_order_completed():
            return profit

        if self._sell_order and self._sell_order.completed():
            #print(f"sell order filled size: {self._sell_order.filled_size} sell order price: {self._sell_order.price} buy order filled size: {self._buy_order.filled_size} buy order price: {self._buy_order.price}")
            #profit = (self._sell_order.filled_size * self._sell_order.price - self._buy_order.filled_size * self._buy_order.price) / (self._buy_order.filled_size * self._buy_order.price) * 100
            profit = (self._sell_order.price - self._buy_order.price) / self._buy_order.price * 100
        elif self._stop_loss_order and self._stop_loss_order.completed():
            #print(f"stop loss order filled size: {self._stop_loss_order.filled_size} stop loss order price: {self._stop_loss_order.price} buy order filled size: {self._buy_order.filled_size} buy order price: {self._buy_order.price}")
            #profit = (self._stop_loss_order.filled_size * self._stop_loss_order.price - self._buy_order.filled_size * self._buy_order.price) / (self._buy_order.filled_size * self._buy_order.price) * 100
            profit = (self._stop_loss_order.price - self._buy_order.price) / self._buy_order.price * 100

        return round(profit, 2)
