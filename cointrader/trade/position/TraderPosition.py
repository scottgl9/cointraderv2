from cointrader.common.Strategy import Strategy
from cointrader.common.Kline import Kline
from cointrader.common.LogLevel import LogLevel
from cointrader.order.Order import Order, OrderSide, OrderType, OrderStatus
from cointrader.order.Orders import Orders
from cointrader.order.OrderRequest import OrderRequest
from cointrader.execute.ExecuteBase import ExecuteBase
from cointrader.execute.pipeline.ExecutePipeline import ExecutePipeline
from cointrader.trade.TraderConfig import TraderConfig
from .PositionBase import PositionBase
import time

class TraderPosition(PositionBase):
    def __init__(self, symbol: str, pid: int, strategy: Strategy, exec_pipe: ExecutePipeline, config: TraderConfig, orders: Orders):
        super().__init__(symbol=symbol, pid=pid, strategy=strategy, exec_pipe=exec_pipe, config=config, orders=orders)


    def create_stop_loss_position(self, stop_price: float, limit_price: float, current_ts: int):
        """
        Create a stop loss order
        """
        # check if we don't have a completed buy order, then we can't create a stop loss order
        if not self.opened():
            return

        #print(f"Creating stop loss order for {self._symbol} stop price: {stop_price} limit price: {limit_price}")
        buy_amount = self._buy_order.filled_size
        #result = self._execute.stop_loss_limit_sell(self._symbol, limit_price=limit_price, stop_price=stop_price, amount=buy_amount)
        oreq = OrderRequest(symbol=self._symbol, side=OrderSide.SELL, size=buy_amount, current_price=self._current_price, current_ts=current_ts)
        oreq.type = OrderType.STOP_LOSS_LIMIT
        oreq.limit_price = limit_price
        oreq.stop_price = stop_price

        # TODO: replace with order pipeline
        #result = self._execute.execute_order(oreq)
        self._exec_pipe.process_order_request(order_request=oreq)
        result = self._exec_pipe.wait_order_result(oreq.rid)
        if result is None:
            print(f"create_stop_loss_position() Stop loss order failed: {self._symbol} {stop_price} {limit_price}")
            return
        self._exec_pipe.completed(oreq.rid)

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
        
        #result = self._execute.status(symbol=self._symbol, order_id=self._stop_loss_order.id, current_price=self._current_price, current_ts=self._current_ts)
        oreq = OrderRequest(symbol=self._symbol, type=OrderType.STATUS, current_price=self._current_price, current_ts=self._current_ts)
        oreq.order_id = self._stop_loss_order.id

        # TODO: replace with order pipeline
        #result = self._execute.execute_order(oreq)
        self._exec_pipe.process_order_request(order_request=oreq)
        result = self._exec_pipe.wait_order_result(oreq.rid)
        if result is None:
            print(f"update_stop_loss_position() Stop loss order failed: {self._symbol} {self._current_price}")
            return None
        self._exec_pipe.completed(oreq.rid)

        self._stop_loss_order.update_order(result)
        self._stop_loss_order.pid = self._pid
        self._orders.update_order(self._symbol, self._stop_loss_order)

        if self._stop_loss_order.rejected() or self._stop_loss_order.unknown():
            print(f"update_stop_loss_position() Stop loss order rejected or unknown: {self._stop_loss_order.msg}")

        return self._stop_loss_order


    def cancel_stop_loss_position(self):
        """
        Cancel the stop loss order
        """
        if not self._stop_loss_order:
            return

        #print(f" stop loss order for {self._symbol} {self._current_price}")
        #result = self._execute.cancel(symbol=self._symbol, order_id=self._stop_loss_order.id, current_price=self._current_price, current_ts=self._current_ts)
        oreq = OrderRequest(symbol=self._symbol, type=OrderType.CANCEL, current_price=self._current_price, current_ts=self._current_ts)
        oreq.order_id = self._stop_loss_order.id

        # TODO: replace with order pipeline
        #result = self._execute.execute_order(oreq)
        self._exec_pipe.process_order_request(order_request=oreq)
        result = self._exec_pipe.wait_order_result(oreq.rid)
        self._exec_pipe.completed(oreq.rid)

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

        oreq = OrderRequest(symbol=self._symbol, side=OrderSide.BUY, size=size, current_price=current_price, current_ts=current_ts)

        if self._config.start_position_type() == OrderType.MARKET.name:
            oreq.type = OrderType.MARKET
            #result = self._execute.market_buy(symbol=self._symbol, amount=size, current_price=current_price, current_ts=current_ts)
        elif self._config.start_position_type() == OrderType.LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, current_price - current_price * limit_order_percent / 100)
            oreq.type = OrderType.LIMIT
            oreq.limit_price = limit_price
            #result = self._execute.limit_buy(symbol=self._symbol, limit_price=limit_price, amount=size)
        elif self._config.start_position_type() == OrderType.STOP_LOSS_LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, current_price + current_price * limit_order_percent / 100)
            stop_loss_limit_percent = self._config.stop_loss_limit_order_percent()
            stop_loss = self._account.round_quote(self._symbol, limit_price - limit_price * stop_loss_limit_percent / 100)
            oreq.type = OrderType.STOP_LOSS_LIMIT
            oreq.limit_price = limit_price
            oreq.stop_price = stop_loss
            #result = self._execute.stop_loss_limit_buy(symbol=self._symbol, limit_price=limit_price, stop_price=stop_loss, amount=size)
        else:
            raise ValueError(f"Invalid start position type: {self._config.start_position_type()}")

        if not self._config.simulate():
            time.sleep(1)

        # TODO: replace with order pipeline
        #result = self._execute.execute_order(oreq)
        self._exec_pipe.process_order_request(order_request=oreq)
        result = self._exec_pipe.wait_order_result(oreq.rid)
        if result is None:
            print(f"open_position() Buy order failed: {self._symbol} {current_price}")
            return
        self._exec_pipe.completed(oreq.rid)

        self._buy_order = Order(symbol=self._symbol)
        self._buy_order.update_order(result)

        if self._buy_order.rejected() or self._buy_order.unknown():
            print(f"open_position() Buy order rejected or unknown: {self._buy_order.msg}")
            return False

        self._buy_order.pid = self._pid
        self._orders.add_order(self._symbol, self._buy_order)

        # if this is a market order, the buy order should already be filled
        if self._buy_order.filled():
            self._opened_position_completed = True
        return True


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
        if self._buy_order.filled():
            self._opened_position_completed = True
            return
        elif self._buy_order.cancelled():
            self.open_position(size=size, current_price=current_price, current_ts=current_ts)
            return
        elif self._buy_order.placed():
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
                if self._config.log_level() >= LogLevel.INFO.value:
                    print(f"Replacing buy order for {self._symbol} current price: {current_price} limit price: {self._buy_order.limit_price}")
                # cancel buy order so we can replace it
                #result = self._execute.cancel(symbol=self._symbol, order_id=self._buy_order.id, current_price=current_price, current_ts=current_ts)
                oreq = OrderRequest(symbol=self._symbol, type=OrderType.CANCEL, current_price=current_price, current_ts=current_ts)
                oreq.order_id = self._buy_order.id

                # TODO: replace with order pipeline
                #result = self._execute.execute_order(oreq)
                self._exec_pipe.process_order_request(order_request=oreq)
                result = self._exec_pipe.wait_order_result(oreq.rid)
                if result is None:
                    print(f"update_buy_position() Cancel Buy order failed: {self._symbol} {current_price}")
                    return
                self._exec_pipe.completed(oreq.rid)

                self._buy_order.update_order(result)
                if self._buy_order.rejected() or self._buy_order.unknown():
                    print(f"update_buy_position() Cancel Buy order rejected or unknown: {self._buy_order.msg}")
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
        if self._sell_order.filled():
            self._closed_position_completed = True
            return
        elif self._sell_order.cancelled():
            self.close_position(current_price=current_price, current_ts=current_ts)
            return
        elif self._sell_order.placed():
            replace_sell_order = False
            replace_order_percent = self._config.replace_sell_order_percent()
            if self._config.end_position_type() == OrderType.LIMIT.name:
                if self._sell_order.limit_price * (1.0 - replace_order_percent / 100.0) > current_price:
                    replace_sell_order = True
            elif self._config.end_position_type() == OrderType.STOP_LOSS_LIMIT.name:
                if self._sell_order.limit_price * (1.0 + replace_order_percent / 100.0) < current_price:
                    replace_sell_order = True

            if replace_sell_order:
                if self._config.log_level() >= LogLevel.INFO.value:
                    print(f"Replacing sell order for {self._symbol} current price: {current_price} limit price: {self._sell_order.limit_price}")
                # cancel sell order so we can replace it
                #result = self._execute.cancel(symbol=self._symbol, order_id=self._sell_order.id, current_price=current_price, current_ts=current_ts)

                oreq = OrderRequest(symbol=self._symbol, type=OrderType.CANCEL, current_price=current_price, current_ts=current_ts)
                oreq.order_id = self._sell_order.id

                # TODO: replace with order pipeline
                #result = self._execute.execute_order(oreq)
                self._exec_pipe.process_order_request(order_request=oreq)
                result = self._exec_pipe.wait_order_result(oreq.rid)
                if result is None:
                    print(f"update_sell_position() Cancel sell order failed: {self._symbol} {current_price}")
                    return
                self._exec_pipe.completed(oreq.rid)

                self._sell_order.update_order(result)

                if self._sell_order.rejected() or self._sell_order.unknown():
                    print(f"update_sell_position() Cancel sell order rejected or unknown: {self._sell_order.msg}")

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

        oreq = OrderRequest(symbol=self._symbol, side=OrderSide.SELL, size=buy_amount, current_price=current_price, current_ts=current_ts)

        if self._config.end_position_type() == OrderType.MARKET.name:
            oreq.type = OrderType.MARKET
            #result = self._execute.market_sell(self._symbol, amount=buy_amount, current_price=current_price, current_ts=current_ts)
        elif self._config.end_position_type() == OrderType.LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, current_price + current_price * limit_order_percent / 100)
            oreq.type = OrderType.LIMIT
            oreq.limit_price = limit_price
            #result = self._execute.limit_sell(self._symbol, limit_price=limit_price, amount=buy_amount)
        elif self._config.end_position_type() == OrderType.STOP_LOSS_LIMIT.name:
            limit_order_percent = self._config.limit_order_percent()
            limit_price = self._account.round_quote(self._symbol, current_price - current_price * limit_order_percent / 100)
            stop_loss_limit_percent = self._config.stop_loss_limit_order_percent()
            stop_loss = self._account.round_quote(self._symbol, limit_price + limit_price * stop_loss_limit_percent / 100)
            oreq.type = OrderType.STOP_LOSS_LIMIT
            oreq.limit_price = limit_price
            oreq.stop_price = stop_loss
            #result = self._execute.stop_loss_limit_sell(self._symbol, limit_price=current_price, stop_price=stop_loss, amount=buy_amount)
        else:
            raise ValueError(f"Invalid end position type: {self._config.end_position_type()}")

        # TODO: replace with order pipeline
        #result = self._execute.execute_order(oreq)
        self._exec_pipe.process_order_request(order_request=oreq)
        result = self._exec_pipe.wait_order_result(oreq.rid)
        if result is None:
            print(f"close_position() Sell order failed: {self._symbol} {current_price}")
            return
        self._exec_pipe.completed(oreq.rid)

        if not self._config.simulate():
            time.sleep(1)

        self._sell_order = Order(symbol=self._symbol)
        self._sell_order.update_order(result)

        if self._sell_order.rejected() or self._sell_order.unknown():
            print(f"close_position() sell order rejected or unknown: {self._sell_order.msg}")

        self._sell_order.pid = self._pid
        self._orders.add_order(self._symbol, self._sell_order)

        # if this is a market order, the buy order should already be filled
        if self._sell_order.status == OrderStatus.FILLED:
            self._closed_position_completed = True


    def market_update(self, current_price: float, current_ts: int):
        """
        Update the position with order status and the current market price
        """
        if self._config.simulate() and self._config.log_level() == LogLevel.DEBUG.value:
            print(f"Updating position for {self._symbol} current price: {current_price}")
        self._current_price = current_price
        self._current_ts = current_ts

        if self._buy_order and not self._buy_order.completed() and not self._buy_order.cancelled():
            #result = self._execute.status(symbol=self._symbol, order_id=self._buy_order.id, current_price=current_price, current_ts=current_ts)
            oreq = OrderRequest(symbol=self._symbol, type=OrderType.STATUS, current_price=current_price, current_ts=current_ts)
            oreq.order_id = self._buy_order.id

            # TODO: replace with order pipeline
            #result = self._execute.execute_order(oreq)
            self._exec_pipe.process_order_request(order_request=oreq)
            result = self._exec_pipe.wait_order_result(oreq.rid)
            if result is None:
                print(f"market_update() Buy order failed: {self._symbol} {current_price}")
                return
            self._exec_pipe.completed(oreq.rid)

            self._buy_order.update_order(result)
            self._buy_order.pid = self._pid
            self._orders.update_order(self._symbol, self._buy_order)
            if self._buy_order.filled():
                if not self._config.simulate():
                    print(f"Buy order filled for {self._symbol} current price: {current_price}")
                self._opened_position_completed = True
            elif self._buy_order.cancelled():
                if not self._config.simulate():
                    print(f"Buy order cancelled for {self._symbol} current price: {current_price}")
                self._buy_order.active = False
                self._orders.update_order_active(symbol=self._symbol, order_id=self._buy_order.id, active=False)
            elif self._buy_order.rejected() or self._buy_order.unknown():
                print(f"market_update() buy order rejected or unknown: {self._buy_order.msg}")

        if not self._closed_position_completed and self._sell_order and not self._sell_order.completed() and not self._sell_order.cancelled():
            #result = self._execute.status(symbol=self._symbol, order_id=self._sell_order.id, current_price=current_price, current_ts=current_ts)
            oreq = OrderRequest(symbol=self._symbol, type=OrderType.STATUS, current_price=current_price, current_ts=current_ts)
            oreq.order_id = self._sell_order.id

            # TODO: replace with order pipeline
            #result = self._execute.execute_order(oreq)
            self._exec_pipe.process_order_request(order_request=oreq)
            result = self._exec_pipe.wait_order_result(oreq.rid)
            if result is None:
                print(f"market_update() Sell order failed: {self._symbol} {current_price}")
                return
            self._exec_pipe.completed(oreq.rid)

            self._sell_order.update_order(result)
            self._buy_order.pid = self._pid
            self._orders.update_order(self._symbol, self._sell_order)
            if self._sell_order.filled():
                if not self._config.simulate():
                    print(f"Sell order filled for {self._symbol} current price: {current_price}")
                # we're closing the position, so set orders to inactive
                self._buy_order.active = False
                self._orders.update_order_active(symbol=self._symbol, order_id=self._buy_order.id, active=False)
                self._sell_order.active = False
                self._orders.update_order_active(symbol=self._symbol, order_id=self._sell_order.id, active=False)
                self._closed_position_completed = True
            elif self._sell_order.cancelled():
                if not self._config.simulate():
                    print(f"Sell order cancelled for {self._symbol} current price: {current_price}")
                self._sell_order.active = False
                self._orders.update_order_active(symbol=self._symbol, order_id=self._sell_order.id, active=False)
            elif self._sell_order.rejected() or self._sell_order.unknown():
                print(f"market_update() sell order rejected or unknown: {self._sell_order.msg}")

        if not self._closed_position_completed and self._stop_loss_order and not self.stop_loss_is_cancelled() and not self._stop_loss_order.completed():
            #print(f"stop loss order: {self._stop_loss_order}")
            #result = self._execute.status(symbol=self._symbol, order_id=self._stop_loss_order.id, current_price=current_price, current_ts=current_ts)
            oreq = OrderRequest(symbol=self._symbol, type=OrderType.STATUS, current_price=current_price, current_ts=current_ts)
            oreq.order_id = self._stop_loss_order.id

            # TODO: replace with order pipeline
            #result = self._execute.execute_order(oreq)
            self._exec_pipe.process_order_request(order_request=oreq)
            result = self._exec_pipe.wait_order_result(oreq.rid)
            if result is None:
                print(f"market_update() Stop loss order failed: {self._symbol} {current_price}")
                return
            self._exec_pipe.completed(oreq.rid)

            self._stop_loss_order.update_order(result)
            self._stop_loss_order.pid = self._pid
            self._orders.update_order(self._symbol, self._stop_loss_order)
            if self._stop_loss_order.filled():
                if not self._config.simulate():
                    print(f"Stop loss order filled for {self._symbol} current price: {current_price}")
                # we're closing the position, so set orders to inactive
                self._buy_order.active = False
                self._orders.update_order_active(symbol=self._symbol, order_id=self._buy_order.id, active=False)
                self._stop_loss_order.active = False
                self._orders.update_order_active(symbol=self._symbol, order_id=self._stop_loss_order.id, active=False)
                self._closed_position_completed = True
            elif self._stop_loss_order.cancelled():
                if not self._config.simulate():
                    print(f"Stop loss order cancelled for {self._symbol} current price: {current_price}")
                self._stop_loss_order.active = False
                self._orders.update_order_active(symbol=self._symbol, order_id=self._stop_loss_order.id, active=False)
            elif self._stop_loss_order.rejected() or self._stop_loss_order.unknown():
                print(f"market_update() stop loss order rejected or unknown: {self._stop_loss_order.msg}")

