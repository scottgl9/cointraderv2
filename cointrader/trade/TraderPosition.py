from cointrader.common.Strategy import Strategy
from cointrader.common.Kline import Kline
from cointrader.order.Order import Order, OrderSide, OrderType, OrderStatus
from cointrader.order.Orders import Orders
from cointrader.execute.ExecuteBase import ExecuteBase
from .TraderConfig import TraderConfig

class TraderPosition(object):
    _symbol = None
    _config: TraderConfig = None
    _buy_order: Order = None
    _sell_order: Order = None
    _stop_loss_order: Order = None

    def __init__(self, symbol: str, id: int, strategy: Strategy, execute: ExecuteBase, config: TraderConfig, orders: Orders):
        self._id = id
        self._symbol = symbol
        self._config = config
        self._orders = orders
        self._buy_order = None
        self._sell_order = None
        self._stop_loss_order = None
        self._strategy = strategy
        self._execute = execute
        self._account = execute.account()
        self._opened_position = False
        self._opened_position_completed = False
        self._closed_position = False
        self._closed_position_completed = False
        self._stop_loss_set = False
        self._entry_price = 0
        self._current_price = 0
        self._buy_price = 0.0
        self._sell_price = 0.0
        self._buy_price_ts = 0
        self._sell_price_ts = 0
        self._stop_loss_price = 0.0
        self._stop_loss_limit_price = 0.0
        self._stop_loss_ts = 0
        self._timestamp = 0
        self._buy_amount = 0.0

    def id(self):
        return self._id

    def opened_position(self):
        return self._opened_position
    
    def closed_position(self):
        return self._closed_position

    def opened_position_completed(self):
        return self._opened_position_completed
    
    def closed_position_completed(self):
        return self._closed_position_completed

    def closed(self):
        if self.sell_order_completed():
            return True
        if self.stop_loss_is_completed():
            print(f"stop loss order completed for {self._symbol}: current: {self._current_price} stop loss: {self._stop_loss_price}")
            return True
        return False

    def opened(self):
        return not self.closed() and self.buy_order_completed()

    def stop_loss_is_set(self):
        return self._stop_loss_order is not None
    
    def stop_loss_price(self):
        return self._stop_loss_price

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
        return self._buy_price

    def buy_info(self):
        return {'price': self._buy_price, 'ts': self._buy_price_ts}

    def sell_info(self):
        return {'price': self._sell_price, 'ts': self._sell_price_ts}

    def open_position(self, price: float, stop_loss: float, size: float, timestamp: int):
        self._opened_position = True
        self._entry_price = price
        self._stop_loss = stop_loss
        self._timestamp = timestamp

        if self._config.start_position_type() == OrderType.MARKET.name:
            result = self._execute.market_buy(symbol=self._symbol, price=price, amount=size)
        elif self._config.start_position_type() == OrderType.LIMIT.name:
            result = self._execute.limit_buy(symbol=self._symbol, price=price, amount=size)
        elif self._config.start_position_type() == OrderType.STOP_LOSS_LIMIT.name:
            result = self._execute.stop_loss_buy(symbol=self._symbol, price=price, stop_price=stop_loss, amount=size)

        self._buy_order = Order(symbol=self._symbol)
        self._buy_order.update_order(result)
        self._orders.add_order(self._symbol, self._buy_order)
        if self._buy_order.status == OrderStatus.FILLED:
            self._buy_amount = self._buy_order.filled_size
            self._buy_price = self._buy_order.price
            self._buy_price_ts = timestamp #self._buy_order.filled_ts
            self._opened_position_completed = True

    def create_stop_loss_position(self, stop_price: float, limit_price: float, timestamp: int):
        """
        Create a stop loss order
        """
        if not self.opened():
            return
        #print(f"Creating stop loss order for {self._symbol} stop price: {stop_price} limit price: {limit_price}")
        self._stop_loss_price = stop_price
        self._stop_loss_limit_price = limit_price
        self._stop_loss_ts = timestamp

        result = self._execute.stop_loss_sell(self._symbol, price=limit_price, stop_price=stop_price, amount=self._buy_amount)

        self._stop_loss_order = Order(symbol=self._symbol)
        self._stop_loss_order.update_order(result)
        self._orders.add_order(self._symbol, self._stop_loss_order)

    def get_buy_position(self) -> Order:
        """
        Get the buy order information
        """
        if not self.opened():
            return None

        return self._buy_order

    def get_stop_loss_position(self) -> Order:
        """
        Get the stop loss order information from exchange (real or simulated)
        """
        if not self._stop_loss_order:
            return None
        
        result = self._execute.status(symbol=self._symbol, order_id=self._stop_loss_order.id, price=self._current_price)
        self._stop_loss_order.update_order(result)

        return self._stop_loss_order

    def cancel_stop_loss_position(self):
        if not self._stop_loss_order:
            return

        result = self._execute.cancel(symbol=self._symbol, order_id=self._stop_loss_order.id, price=self._current_price)
        self._stop_loss_order.update_order(result)

    def close_position(self, price: float, timestamp: int):
        self._closed_position = True
        self.current_price = price
        self._timestamp = timestamp

        if self._config.end_position_type() == OrderType.MARKET.name:
            result = self._execute.market_sell(self._symbol, price=price, amount=self._buy_amount)
        elif self._config.end_position_type() == OrderType.LIMIT.name:
            result = self._execute.limit_sell(self._symbol, price=price, amount=self._buy_amount)
        elif self._config.end_position_type() == OrderType.STOP_LOSS_LIMIT.name:
            result = self._execute.stop_loss_sell(self._symbol, price=price, stop_price=self._stop_loss, amount=self._buy_amount)

        self._sell_order = Order(symbol=self._symbol)
        self._sell_order.update_order(result)

        if self._sell_order.status == OrderStatus.FILLED:
            self._sell_price = self._sell_order.price
            self._sell_price_ts = timestamp #self._sell_order.filled_ts
            self._closed_position_completed = True

    def market_update(self, current_price: float):
        """
        Update the position with order status and the current market price
        """
        self._current_price = current_price

        if self._buy_order and not self.buy_order_completed():
            result = self._execute.status(symbol=self._symbol, order_id=self._buy_order.id, price=self._current_price)
            self._buy_order.update_order(result)

        if self._sell_order and not self._sell_order.completed():
            result = self._execute.status(symbol=self._symbol, order_id=self._sell_order.id, price=self._current_price)
            self._sell_order.update_order(result)

        if self._stop_loss_order and not self.stop_loss_is_completed():
            #print(f"stop loss order: {self._stop_loss_order}")
            result = self._execute.status(symbol=self._symbol, order_id=self._stop_loss_order.id, price=self._current_price)
            self._stop_loss_order.update_order(result)

    def current_position_percent(self, price: float):
        """
        Calculate the current position percent
        """
        if not self.buy_order_completed():
            return 0.0
        return (price - self._buy_price) / self._buy_price * 100

    def profit_percent(self):
        profit = 0.0

        if not self.buy_order_completed():
            return profit

        if self._sell_order and self._sell_order.completed():
            #print(f"sell order filled size: {self._sell_order.filled_size} sell order price: {self._sell_order.price} buy order filled size: {self._buy_order.filled_size} buy order price: {self._buy_order.price}")
            profit = (self._sell_order.filled_size * self._sell_order.price - self._buy_order.filled_size * self._buy_order.price) / (self._buy_order.filled_size * self._buy_order.price) * 100
        elif self._stop_loss_order and self._stop_loss_order.completed():
            #print(f"stop loss order filled size: {self._stop_loss_order.filled_size} stop loss order price: {self._stop_loss_order.price} buy order filled size: {self._buy_order.filled_size} buy order price: {self._buy_order.price}")
            profit = (self._stop_loss_order.filled_size * self._stop_loss_order.price - self._buy_order.filled_size * self._buy_order.price) / (self._buy_order.filled_size * self._buy_order.price) * 100

        return round(profit, 2)
