from cointrader.common.Strategy import Strategy
from cointrader.common.Kline import Kline
from cointrader.order.Order import Order, OrderSide, OrderType, OrderStatus
from cointrader.order.Orders import Orders
from cointrader.execute.ExecuteBase import ExecuteBase
from .TraderConfig import TraderConfig

class TraderPosition(object):
    _symbol = None
    _config = None
    def __init__(self, symbol: str, strategy: Strategy, execute: ExecuteBase, config: TraderConfig):
        self._symbol = symbol
        self._config = config
        self._order = None
        self._strategy = strategy
        self._execute = execute
        self._closed_position = False
        self._stop_loss_set = False
        self._entry_price = 0
        self._current_price = 0
        self._stop_loss = 0
        self._timestamp = 0

    def open_position(self, price: float, stop_loss: float, size: float, timestamp: int):
        self._entry_price = price
        self._stop_loss = stop_loss
        self._timestamp = timestamp
        result = self._execute.market_buy(self._symbol, size)
        print(result)

    def get_position(self) -> Order:
        return self._order

    def close_position(self, price: float, timestamp: int):
        self._closed_position = True
        self.current_price = price
        self._timestamp = timestamp
        result = self._execute.market_sell(self._symbol, self._order.quantity)
        print(result)

    def market_update(self, kline: Kline):
        self._current_price = kline.close
    
    def closed(self):
        return self._closed_position
