from cointrader.common.Strategy import Strategy
from cointrader.common.Kline import Kline
from cointrader.order.Order import Order, OrderSide, OrderType, OrderStatus
from cointrader.order.Orders import Orders
from cointrader.execute.ExecuteBase import ExecuteBase
from .TraderConfig import TraderConfig
from decimal import Decimal

class TraderPosition(object):
    _symbol = None
    _config = None
    def __init__(self, symbol: str, strategy: Strategy, execute: ExecuteBase, config: TraderConfig):
        self._symbol = symbol
        self._config = config
        self._buy_order = None
        self._sell_order = None
        self._strategy = strategy
        self._execute = execute
        self._closed_position = False
        self._stop_loss_set = False
        self._entry_price = 0
        self._current_price = 0
        self._stop_loss = 0
        self._timestamp = 0

    def open_position(self, price: Decimal, stop_loss: Decimal, size: Decimal, timestamp: int):
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

    def get_position(self) -> Order:
        return self._order

    def close_position(self, price: Decimal, timestamp: int):
        self.current_price = price
        self._timestamp = timestamp

        if self._config.end_position_type() == OrderType.MARKET.name:
            result = self._execute.market_sell(self._symbol, price=price, amount=self._buy_order.filled_size)
        elif self._config.end_position_type() == OrderType.LIMIT.name:
            result = self._execute.limit_sell(self._symbol, price=price, amount=self._buy_order.filled_size)
        elif self._config.end_position_type() == OrderType.STOP_LOSS_LIMIT.name:
            result = self._execute.stop_loss_sell(self._symbol, price=price, stop_price=self._stop_loss, amount=self._buy_order.filled_size)

        self._sell_order = Order(symbol=self._symbol)
        self._sell_order.update_order(result)

    def market_update(self, kline: Kline):
        self._current_price = kline.close

        if self._buy_order and not self._buy_order.completed():
            result = self._execute.status(symbol=self._symbol, order_id=self._buy_order.id, price=self._current_price)
            self._buy_order.update_order(result)

        if self._sell_order and not self._sell_order.completed():
            result = self._execute.status(symbol=self._symbol, order_id=self._sell_order.id, price=self._current_price)
            self._sell_order.update_order(result)
    
    def closed(self):
        return self._sell_order and self._sell_order.completed()
    
    def profit_percent(self):
        profit = 0.0
        if not self._sell_order or not self._sell_order:
            return profit
        if self._buy_order.completed() and self._sell_order.completed():
            profit = (self._sell_order.filled_size * self._sell_order.price - self._buy_order.filled_size * self._buy_order.price) / (self._buy_order.filled_size * self._buy_order.price) * 100

        return round(profit, 2)
