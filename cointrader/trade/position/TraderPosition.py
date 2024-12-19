from cointrader.common.Strategy import Strategy
from cointrader.common.Kline import Kline
from cointrader.order.Order import Order, OrderSide, OrderType, OrderStatus
from cointrader.order.Orders import Orders
from cointrader.execute.ExecuteBase import ExecuteBase
from cointrader.trade.TraderConfig import TraderConfig
from .PositionBase import PositionBase
import time

class TraderPosition(PositionBase):
    def __init__(self, symbol: str, pid: int, strategy: Strategy, execute: ExecuteBase, config: TraderConfig, orders: Orders):
        super().__init__(symbol=symbol, pid=pid, strategy=strategy, execute=execute, config=config, orders=orders)


    def create_stop_loss_position(self, stop_price: float, limit_price: float, current_ts: int):
        """
        Create a stop loss order
        """
        # check if we don't have a completed buy order, then we can't create a stop loss order
        if not self.opened():
            return

        #print(f"Creating stop loss order for {self._symbol} stop price: {stop_price} limit price: {limit_price}")
        buy_amount = self._buy_order.filled_size
        result = self._execute.stop_loss_limit_sell(self._symbol, limit_price=limit_price, stop_price=stop_price, amount=buy_amount)

        self._stop_loss_order = Order(symbol=self._symbol)
        self._stop_loss_order.update_order(result)
        self._stop_loss_order.pid = self._pid
        self._orders.add_order(self._symbol, self._stop_loss_order)


    def update_stop_loss_position(self) -> Order:
        """
        Get the stop loss order information from exchange (real or simulated)
        """
        if not self._stop_loss_order:
            return None
        
        result = self._execute.status(symbol=self._symbol, order_id=self._stop_loss_order.id, current_price=self._current_price, current_ts=self._current_ts)
        self._stop_loss_order.update_order(result)
        self._stop_loss_order.pid = self._pid
        self._orders.update_order(self._symbol, self._stop_loss_order)

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
        self._last_stop_loss_order.pid = self._pid
        self._last_stop_loss_order.active = False
        self._orders.update_order(self._symbol, self._last_stop_loss_order)
        self._stop_loss_order = None


    def open_position(self, size: float, current_price: float, current_ts: int):
        """
        Open a position with a buy order
        """
        if not self._config.simulate():
            print(f"Opening position for {self._symbol} current price: {current_price}, current ts: {current_ts}")
        self._current_price = current_price
        self._current_ts = current_ts
        self._opened_position = True
        self._entry_price = current_price

        if self._config.start_position_type() == OrderType.MARKET.name:
            result = self._execute.market_buy(symbol=self._symbol, amount=size, current_price=current_price, current_ts=current_ts)
        elif self._config.start_position_type() == OrderType.LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, current_price - current_price * limit_order_percent / 100)
            result = self._execute.limit_buy(symbol=self._symbol, limit_price=limit_price, amount=size)
        elif self._config.start_position_type() == OrderType.STOP_LOSS_LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, current_price + current_price * limit_order_percent / 100)
            stop_loss_percent = self._config.stop_loss_percent()
            stop_loss = self._account.round_quote(self._symbol, current_price + current_price * stop_loss_percent / 100)
            result = self._execute.stop_loss_limit_buy(symbol=self._symbol, limit_price=limit_price, stop_price=stop_loss, amount=size)
        else:
            raise ValueError(f"Invalid start position type: {self._config.start_position_type()}")

        if not self._config.simulate():
            time.sleep(1)

        self._buy_order = Order(symbol=self._symbol)
        self._buy_order.update_order(result)
        self._buy_order.pid = self._pid
        self._orders.add_order(self._symbol, self._buy_order)

        # if this is a market order, the buy order should already be filled
        if self._buy_order.status == OrderStatus.FILLED:
            self._opened_position_completed = True


    def update_buy_position(self, size: float, current_price: float, current_ts: int):
        """
        For limit and stop loss limit orders, check if the buy order should be cancelled and replaced
        """
        if self._config.start_position_type() == OrderType.MARKET.name:
            return

        if not self._buy_order or self.buy_order_completed():
            return

        # result = self._execute.status(symbol=self._symbol, order_id=self._buy_order.id, current_price=current_price, current_ts=current_ts)
        # self._buy_order.update_order(result)
        if self._buy_order.status == OrderStatus.FILLED:
            self._opened_position_completed = True
            return
        elif self._buy_order.status == OrderStatus.CANCELLED:
            self.open_position(size=size, current_price=current_price, current_ts=current_ts)
            return
        elif self._buy_order.status == OrderStatus.PLACED:
            #print(f"Updating buy order for {self._symbol} current price: {current_price} limit price: {self._buy_order.limit_price}")

            replace_buy_order = False
            replace_order_percent = self._config.replace_buy_order_percent()
            if self._config.start_position_type() == OrderType.LIMIT.name:
                if self._buy_order.limit_price * (1.0 + replace_order_percent / 100.0) < current_price:
                    replace_buy_order = True
            elif self._config.start_position_type() == OrderType.STOP_LOSS_LIMIT.name:
                if self._buy_order.limit_price * (1.0 - replace_order_percent / 100.0) > current_price:
                    replace_buy_order = True

            if replace_buy_order:
                print(f"Replacing buy order for {self._symbol} current price: {current_price} limit price: {self._buy_order.limit_price}")
                # cancel buy order so we can replace it
                result = self._execute.cancel(symbol=self._symbol, order_id=self._buy_order.id, current_price=current_price, current_ts=current_ts)
                self._buy_order.update_order(result)
                self._buy_order.pid = self._pid
                self._buy_order.active = False
                self._orders.update_order(self._symbol, self._buy_order)
                if not self._config.simulate():
                    time.sleep(1)
                self.open_position(size=size, current_price=current_price, current_ts=current_ts)
    

    def update_sell_position(self, current_price: float, current_ts: int):
        """
        For limit and stop loss limit orders, check if the sell order should be cancelled and replaced
        """
        if not self._sell_order or self.sell_order_completed():
            return
        #result = self._execute.status(symbol=self._symbol, order_id=self._sell_order.id, current_price=current_price, current_ts=current_ts)
        #self._sell_order.update_order(result)
        if self._sell_order.status == OrderStatus.FILLED:
            self._closed_position_completed = True
            return
        elif self._sell_order.status == OrderStatus.CANCELLED:
            self.close_position(current_price=current_price, current_ts=current_ts)
            return
        elif self._sell_order.status == OrderStatus.PLACED:
            replace_sell_order = False
            replace_order_percent = self._config.replace_sell_order_percent()
            if self._config.end_position_type() == OrderType.LIMIT.name:
                if self._sell_order.limit_price * (1.0 - replace_order_percent / 100.0) > current_price:
                    replace_sell_order = True
            elif self._config.end_position_type() == OrderType.STOP_LOSS_LIMIT.name:
                if self._sell_order.limit_price * (1.0 + replace_order_percent / 100.0) < current_price:
                    replace_sell_order = True

            if replace_sell_order:
                print(f"Replacing sell order for {self._symbol} current price: {current_price} limit price: {self._sell_order.limit_price}")
                # cancel sell order so we can replace it
                result = self._execute.cancel(symbol=self._symbol, order_id=self._sell_order.id, current_price=current_price, current_ts=current_ts)
                self._sell_order.update_order(result)
                self._sell_order.pid = self._pid
                self._sell_order.active = False
                self._orders.update_order(self._symbol, self._sell_order)
                if not self._config.simulate():
                    time.sleep(1)
                self.close_position(current_price=current_price, current_ts=current_ts)


    def close_position(self, current_price: float, current_ts: int):
        """
        Close the position with a sell order
        """
        if not self._config.simulate():
            print(f"Closing position for {self._symbol} current price: {current_price}, current ts: {current_ts}")
        self._closed_position = True
        self._current_price = current_price
        self._current_ts = current_ts

        # check if we have an open stop loss order, if so we need to cancel it
        if self._stop_loss_order:
            if not self.stop_loss_is_completed():
                # check if the stop loss order is filled
                self.update_stop_loss_position()
                if self.stop_loss_is_completed():
                    # stop loss order already filled, so position is closed
                    self._closed_position_completed = True
                    return
                else:
                    # cancel stop loss order so we can place a new sell order
                    self.cancel_stop_loss_position()
                    if not self._config.simulate():
                        time.sleep(1)
            else:
                # stop loss order already filled, so position is closed
                self._closed_position_completed = True
                return

        if self._sell_order and self._sell_order.completed():
            self._closed_position_completed = True
            return

        buy_amount = self._buy_order.filled_size

        if self._config.end_position_type() == OrderType.MARKET.name:
            result = self._execute.market_sell(self._symbol, amount=buy_amount, current_price=current_price, current_ts=current_ts)
        elif self._config.end_position_type() == OrderType.LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, current_price + current_price * limit_order_percent / 100)
            result = self._execute.limit_sell(self._symbol, limit_price=limit_price, amount=buy_amount)
        elif self._config.end_position_type() == OrderType.STOP_LOSS_LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, current_price - current_price * limit_order_percent / 100)
            stop_loss_percent = self._config.stop_loss_percent()
            stop_loss = self._account.round_quote(self._symbol, current_price - current_price * stop_loss_percent / 100)
            result = self._execute.stop_loss_limit_sell(self._symbol, limit_price=current_price, stop_price=stop_loss, amount=buy_amount)
        else:
            raise ValueError(f"Invalid end position type: {self._config.end_position_type()}")

        if not self._config.simulate():
            time.sleep(1)

        self._sell_order = Order(symbol=self._symbol)
        self._sell_order.update_order(result)
        self._sell_order.pid = self._pid
        self._orders.add_order(self._symbol, self._sell_order)

        # if this is a market order, the buy order should already be filled
        if self._sell_order.status == OrderStatus.FILLED:
            self._closed_position_completed = True


    def market_update(self, current_price: float, current_ts: int):
        """
        Update the position with order status and the current market price
        """
        #if self._config.verbose():
        #    print(f"Updating position for {self._symbol} current price: {current_price}")
        self._current_price = current_price
        self._current_ts = current_ts

        if self._buy_order and not self._buy_order.completed():
            result = self._execute.status(symbol=self._symbol, order_id=self._buy_order.id, current_price=current_price, current_ts=current_ts)
            self._buy_order.update_order(result)
            self._buy_order.pid = self._pid
            self._orders.update_order(self._symbol, self._buy_order)
            if self._buy_order.status == OrderStatus.FILLED:
                self._opened_position_completed = True

        if not self._closed_position_completed and self._sell_order and not self._sell_order.completed():
            result = self._execute.status(symbol=self._symbol, order_id=self._sell_order.id, current_price=current_price, current_ts=current_ts)
            self._sell_order.update_order(result)
            self._buy_order.pid = self._pid
            self._orders.update_order(self._symbol, self._sell_order)
            if self._sell_order.status == OrderStatus.FILLED:
                # we're closing the position, so set orders to inactive
                self._buy_order.active = False
                self._orders.update_order_active(symbol=self._symbol, order_id=self._buy_order.id, active=False)
                self._sell_order.active = False
                self._orders.update_order_active(symbol=self._symbol, order_id=self._sell_order.id, active=False)
                self._closed_position_completed = True

        if not self._closed_position_completed and self._stop_loss_order and not self.stop_loss_is_cancelled() and not self._stop_loss_order.completed():
            #print(f"stop loss order: {self._stop_loss_order}")
            result = self._execute.status(symbol=self._symbol, order_id=self._stop_loss_order.id, current_price=current_price, current_ts=current_ts)
            self._stop_loss_order.update_order(result)
            self._stop_loss_order.pid = self._pid
            self._orders.update_order(self._symbol, self._stop_loss_order)
            if self._stop_loss_order.status == OrderStatus.FILLED:
                # we're closing the position, so set orders to inactive
                self._buy_order.active = False
                self._orders.update_order_active(symbol=self._symbol, order_id=self._buy_order.id, active=False)
                self._stop_loss_order.active = False
                self._orders.update_order_active(symbol=self._symbol, order_id=self._stop_loss_order.id, active=False)
                self._closed_position_completed = True
