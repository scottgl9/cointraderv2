# Implement simulate trading execution for backtesting
from cointrader.client.TraderClientBase import TraderClientBase
from .ExecuteBase import ExecuteBase
from cointrader.order.OrderResult import OrderResult
from cointrader.order.Order import OrderStatus, OrderType, OrderSide
from cointrader.account.AccountBase import AccountBase
import uuid

class TraderExecuteSimulate(ExecuteBase):
    def __init__(self, client: TraderClientBase, account: AccountBase):
        self._client = client
        self._account = account
        self._orders = {}

    def market_buy(self, symbol: str, price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.FILLED
        result.side = OrderSide.BUY
        result.type = OrderType.MARKET
        result.price = price
        result.size = amount
        result.filled_size = amount

        # simulate account update
        base = self._client.info_ticker_get_base(symbol)
        quote = self._client.info_ticker_get_quote(symbol)

        # Update base balance
        base_balance, base_balance_hold = self._account.get_asset_balance(base)
        self._account.update_asset_balance(base, base_balance + amount, base_balance_hold)
        
        # Update quote balance
        quote_balance, quote_balance_hold = self._account.get_asset_balance(quote)
        self._account.update_asset_balance(quote, quote_balance - price * amount, quote_balance_hold)

        self._orders[result.id] = result
        return result
    
    def market_sell(self, symbol: str, price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.FILLED
        result.side = OrderSide.SELL
        result.type = OrderType.MARKET
        result.price = price
        result.size = amount
        result.filled_size = amount

        # simulate account update
        base = self._client.info_ticker_get_base(symbol)
        quote = self._client.info_ticker_get_quote(symbol)

        # Update base balance
        base_balance, base_balance_hold = self._account.get_asset_balance(base)
        self._account.update_asset_balance(base, base_balance - amount, base_balance_hold)
        
        # Update quote balance
        quote_balance, quote_balance_hold = self._account.get_asset_balance(quote)
        self._account.update_asset_balance(quote, quote_balance + price * amount, quote_balance_hold)

        self._orders[result.id] = result
        return result
    
    def limit_buy(self, symbol: str, price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.BUY
        result.type = OrderType.LIMIT
        result.price = price
        result.size = amount
        result.filled_size = 0.0
        self._orders[result.id] = result
        return result

    def limit_sell(self, symbol: str, price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.SELL
        result.type = OrderType.LIMIT
        result.price = price
        result.size = amount
        result.filled_size = 0.0
        self._orders[result.id] = result
        return result

    def stop_loss_buy(self, symbol: str, price: float, stop_price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.BUY
        result.type = OrderType.STOP_LOSS_LIMIT
        result.price = price
        result.limit_price = stop_price
        result.size = amount
        result.filled_size = 0.0
        self._orders[result.id] = result
        return result
    
    def stop_loss_sell(self, symbol: str, price: float, stop_price: float, amount: float) -> OrderResult:
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.SELL
        result.type = OrderType.STOP_LOSS_LIMIT
        result.price = price
        result.limit_price = stop_price
        result.size = amount
        result.filled_size = 0.0
        self._orders[result.id] = result
        return result

    def status(self, symbol: str, order_id: str, price: float) -> OrderResult:
        if order_id in self._orders:
            return self._orders[order_id]
        return None

    def cancel(self, symbol: str, order_id: str, price: float) -> OrderResult:
        raise NotImplementedError
