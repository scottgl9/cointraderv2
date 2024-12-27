# Base class for executing trades
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from cointrader.order.OrderResult import OrderResult
from cointrader.order.Order import Order
from cointrader.order.OrderRequest import OrderRequest
from cointrader.order.enum.OrderType import OrderType
from cointrader.order.enum.OrderSide import OrderSide
from cointrader.account.AccountBase import AccountBase

class ExecuteBase(object):
    _exchange = None
    _config = None

    def __init__(self, exchange: TraderExchangeBase):
        self._exchange = exchange

    def account(self) -> AccountBase:
        raise NotImplementedError

    def execute_order(self, order_request: OrderRequest) -> OrderResult:
        """
        Execute an order (buy, sell, status, cancel)
        """
        if order_request.type == OrderType.MARKET:
            if order_request.side == OrderSide.BUY:
                return self.market_buy(symbol=order_request.symbol, amount=order_request.size, current_price=order_request.current_price, current_ts=order_request.current_ts)
            elif order_request.side == OrderSide.SELL:
                return self.market_sell(symbol=order_request.symbol, amount=order_request.size, current_price=order_request.current_price, current_ts=order_request.current_ts)
        elif order_request.type == OrderType.LIMIT:
            if order_request.side == OrderSide.BUY:
                return self.limit_buy(symbol=order_request.symbol, limit_price=order_request.limit_price, amount=order_request.size)
            elif order_request.side == OrderSide.SELL:
                return self.limit_sell(symbol=order_request.symbol, limit_price=order_request.limit_price, amount=order_request.size)
        elif order_request.type == OrderType.STOP_LOSS_LIMIT:
            if order_request.side == OrderSide.BUY:
                return self.stop_loss_limit_buy(symbol=order_request.symbol, limit_price=order_request.limit_price, stop_price=order_request.stop_price, amount=order_request.size)
            elif order_request.side == OrderSide.SELL:
                return self.stop_loss_limit_sell(symbol=order_request.symbol, limit_price=order_request.limit_price, stop_price=order_request.stop_price, amount=order_request.size)
        elif order_request.type == OrderType.STATUS:
            return self.status(symbol=order_request.symbol, order_request_id=order_request.id, current_price=order_request.current_price, current_ts=order_request.current_ts)
        elif order_request.type == OrderType.CANCEL:
            return self.cancel(symbol=order_request.symbol, order_request_id=order_request.id, current_price=order_request.current_price, current_ts=order_request.current_ts)
        else:
            raise ValueError("execute_order(): Invalid order type")

    def market_buy(self, symbol: str, amount: float, current_price: float, current_ts: int) -> OrderResult:
        raise NotImplementedError
    
    def market_sell(self, symbol: str, amount: float, current_price: float, current_ts: int) -> OrderResult:
        raise NotImplementedError

    def limit_buy(self, symbol: str, limit_price: float, amount: float) -> OrderResult:
        raise NotImplementedError
    
    def limit_sell(self, symbol: str, limit_price: float, amount: float) -> OrderResult:
        raise NotImplementedError
    
    def stop_loss_limit_buy(self, symbol: str, limit_price: float, stop_price: float, amount: float) -> OrderResult:
        raise NotImplementedError
    
    def stop_loss_limit_sell(self, symbol: str, limit_price: float, stop_price: float, amount: float) -> OrderResult:
        raise NotImplementedError
    
    def status(self, symbol: str, order_id: str, current_price: float, current_ts: int) -> OrderResult:
        """
        Get order status
        """
        raise NotImplementedError
    
    def cancel(self, symbol: str, order_id: str, current_price: float, current_ts: int) -> OrderResult:
        """
        Cancel an order
        """
        raise NotImplementedError
