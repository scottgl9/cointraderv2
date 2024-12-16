from cointrader.common.Strategy import Strategy
from cointrader.common.Kline import Kline
from cointrader.order.Order import Order, OrderSide, OrderType, OrderStatus
from cointrader.order.Orders import Orders
from cointrader.execute.ExecuteBase import ExecuteBase
from .TraderConfig import TraderConfig
import time

class TraderPosition(object):
    _symbol = None
    _config: TraderConfig = None
    _buy_order: Order = None
    _sell_order: Order = None
    _stop_loss_order: Order = None
    _last_stop_loss_order: Order = None

    def __init__(self, symbol: str, id: int, strategy: Strategy, execute: ExecuteBase, config: TraderConfig, orders: Orders):
        self._id = id
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
        self._stop_loss_set = False
        self._entry_price = 0
        self._current_price = 0
        self._current_ts = 0
        self._buy_price = 0.0
        self._sell_price = 0.0
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
            return True
        return False

    def opened(self):
        return not self.closed() and self.buy_order_completed()

    def stop_loss_is_set(self):
        return self._stop_loss_order is not None
    
    def stop_loss_price(self):
        return self._stop_loss_price
    
    def stop_loss_limit_price(self):
        return self._stop_loss_limit_price

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

    def open_position(self, price: float, size: float, timestamp: int, current_price: float):
        """
        Open a position with a buy order
        """
        self._current_price = current_price
        self._current_ts = timestamp
        self._opened_position = True
        self._entry_price = price
        self._timestamp = timestamp

        if self._config.start_position_type() == OrderType.MARKET.name:
            result = self._execute.market_buy(symbol=self._symbol, amount=size, current_price=self._current_price, current_ts=self._current_ts)
        elif self._config.start_position_type() == OrderType.LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, price - price * limit_order_percent / 100)
            result = self._execute.limit_buy(symbol=self._symbol, limit_price=limit_price, amount=size)
        elif self._config.start_position_type() == OrderType.STOP_LOSS_LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, price + price * limit_order_percent / 100)
            stop_loss_percent = self._config.stop_loss_percent()
            stop_loss = self._account.round_quote(self._symbol, price + price * stop_loss_percent / 100)
            result = self._execute.stop_loss_limit_buy(symbol=self._symbol, limit_price=limit_price, stop_price=stop_loss, amount=size)

        if not self._config.simulate():
            time.sleep(1)

        self._buy_order = Order(symbol=self._symbol)
        self._buy_order.update_order(result)
        self._orders.add_order(self._symbol, self._buy_order)
        if self._buy_order.status == OrderStatus.FILLED:
            self._buy_amount = self._buy_order.filled_size
            self._buy_price = self._buy_order.price
            self._buy_price_ts = self._buy_order.filled_ts
            self._opened_position_completed = True

    def update_buy_position(self, price: float, size: float, current_price: float, current_ts: int):
        """
        For limit and stop loss limit orders, check if the buy order should be cancelled and replaced
        """
        if self._config.start_position_type() == OrderType.MARKET.name:
            return

        if not self._buy_order or self.buy_order_completed():
            return
        result = self._execute.status(symbol=self._symbol, order_id=self._buy_order.id, current_price=current_price, current_ts=current_ts)
        self._buy_order.update_order(result)
        if self._buy_order.status == OrderStatus.FILLED:
            self._buy_price = self._buy_order.price
            self._opened_position_completed = True
            return
        elif self._buy_order.status == OrderStatus.CANCELLED:
            self.open_position(price, size, current_ts, current_price)
            return
        elif self._buy_order.status == OrderStatus.PLACED:
            # cancel buy order so we can replace it
            result = self._execute.cancel(symbol=self._symbol, order_id=self._buy_order.id, current_price=current_price, current_ts=current_ts)
            self._buy_order.update_order(result)
            if not self._config.simulate():
                time.sleep(1)
            self.open_position(price, size, current_ts, current_price)
    
    def update_sell_position(self, price: float, current_price: float, current_ts: int):
        """
        For limit and stop loss limit orders, check if the sell order should be cancelled and replaced
        """
        if not self._sell_order or self.sell_order_completed():
            return
        result = self._execute.status(symbol=self._symbol, order_id=self._sell_order.id, current_price=current_price, current_ts=current_ts)
        self._sell_order.update_order(result)
        if self._sell_order.status == OrderStatus.FILLED:
            self._sell_price = self._sell_order.price
            self._closed_position_completed = True
            return
        elif self._sell_order.status == OrderStatus.CANCELLED:
            self.close_position(price, current_ts, current_price)
            return
        elif self._sell_order.status == OrderStatus.PLACED:
            # cancel sell order so we can replace it
            result = self._execute.cancel(symbol=self._symbol, order_id=self._sell_order.id, current_price=current_price, current_ts=current_ts)
            self._sell_order.update_order(result)
            if not self._config.simulate():
                time.sleep(1)
            self.close_position(price, current_ts, current_price)

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

        result = self._execute.stop_loss_limit_sell(self._symbol, limit_price=limit_price, stop_price=stop_price, amount=self._buy_amount)

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
        
        result = self._execute.status(symbol=self._symbol, order_id=self._stop_loss_order.id, current_price=self._current_price, current_ts=self._current_ts)
        self._stop_loss_order.update_order(result)

        return self._stop_loss_order

    def cancel_stop_loss_position(self):
        """
        Cancel the stop loss order
        """
        if not self._stop_loss_order:
            return

        #print(f" stop loss order for {self._symbol} {self._current_price}")
        result = self._execute.cancel(symbol=self._symbol, order_id=self._stop_loss_order.id, current_price=self._current_price, current_ts=self._current_ts)
        self._last_stop_loss_order = Order(symbol=self._symbol)
        self._last_stop_loss_order.update_order(result)
        self._stop_loss_order = None

    def close_position(self, price: float, timestamp: int, current_price: float):
        """
        Close the position with a sell order
        """
        self._closed_position = True
        self._current_price = price
        self._current_ts = timestamp

        # check if we have an open stop loss order, if so we need to cancel it
        if self._stop_loss_order:
            if not self.stop_loss_is_completed():
                # check if the stop loss order is filled
                self.get_stop_loss_position()
                if self.stop_loss_is_completed():
                    # stop loss order already filled, so position is closed
                    self._closed_position_completed = True
                    return
                else:
                    self.cancel_stop_loss_position()
                    if not self._config.simulate():
                        time.sleep(1)
            else:
                # stop loss order already filled, so position is closed
                self._closed_position_completed = True
                return

        if self._config.end_position_type() == OrderType.MARKET.name:
            result = self._execute.market_sell(self._symbol, amount=self._buy_amount, current_price=price, current_ts=self._current_ts)
        elif self._config.end_position_type() == OrderType.LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, price + price * limit_order_percent / 100)
            result = self._execute.limit_sell(self._symbol, limit_price=limit_price, amount=self._buy_amount)
        elif self._config.end_position_type() == OrderType.STOP_LOSS_LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, price - price * limit_order_percent / 100)
            stop_loss_percent = self._config.stop_loss_percent()
            stop_loss = self._account.round_quote(self._symbol, price - price * stop_loss_percent / 100)
            result = self._execute.stop_loss_limit_sell(self._symbol, limit_price=price, stop_price=stop_loss, amount=self._buy_amount)

        if not self._config.simulate():
            time.sleep(1)

        self._sell_order = Order(symbol=self._symbol)
        self._sell_order.update_order(result)

        if self._sell_order.status == OrderStatus.FILLED:
            self._sell_price = self._sell_order.price
            self._sell_price_ts = self._sell_order.filled_ts
            self._closed_position_completed = True

    def market_update(self, current_price: float, current_ts: int):
        """
        Update the position with order status and the current market price
        """
        #if self._config.verbose():
        #    print(f"Updating position for {self._symbol} current price: {current_price}")
        self._current_price = current_price
        self._current_ts = current_ts

        if self._buy_order and not self.buy_order_completed():
            result = self._execute.status(symbol=self._symbol, order_id=self._buy_order.id, current_price=current_price, current_ts=current_ts)
            prev_status = self._buy_order.status
            self._buy_order.update_order(result)
            if self._buy_order.status == OrderStatus.FILLED and prev_status != OrderStatus.FILLED:
                self._buy_price = self._buy_order.price
                self._opened_position_completed = True

        if self._sell_order and not self._sell_order.completed():
            result = self._execute.status(symbol=self._symbol, order_id=self._sell_order.id, current_price=current_price, current_ts=current_ts)
            prev_status = self._buy_order.status
            self._sell_order.update_order(result)
            if self._sell_order.status == OrderStatus.FILLED and prev_status != OrderStatus.FILLED:
                self._sell_price = self._sell_order.price
                self._closed_position_completed = True

        if self._stop_loss_order and not self.stop_loss_is_completed():
            #print(f"stop loss order: {self._stop_loss_order}")
            result = self._execute.status(symbol=self._symbol, order_id=self._stop_loss_order.id, current_price=current_price, current_ts=current_ts)
            self._stop_loss_order.update_order(result)
            prev_status = self._buy_order.status
            if self._stop_loss_order.status == OrderStatus.FILLED and prev_status != OrderStatus.FILLED:
                self._stop_loss_price = self._stop_loss_order.price
                self._stop_loss_ts = self._stop_loss_order.filled_ts
                self._closed_position_completed = True

    def current_position_percent(self, price: float):
        """
        Calculate the current position percent for an open position
        """
        if not self.buy_order_completed():
            return 0.0
        return (price - self._buy_price) / self._buy_price * 100

    def profit_percent(self):
        """
        Calculate the profit percent for a closed position
        """
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
