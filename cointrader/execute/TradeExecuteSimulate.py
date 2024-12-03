# Implement simulate trading execution for backtesting
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from .ExecuteBase import ExecuteBase
from cointrader.order.OrderResult import OrderResult
from cointrader.order.Order import OrderStatus, OrderType, OrderSide
from cointrader.account.AccountBase import AccountBase
import uuid

class TraderExecuteSimulate(ExecuteBase):
    def __init__(self, exchange: TraderExchangeBase, account: AccountBase):
        self._exchange = exchange
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
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Update base balance
        base_balance, base_balance_hold = self._account.get_asset_balance(base)
        new_base_balance = self._account.round_base(symbol, base_balance + amount)
        self._account.update_asset_balance(base, new_base_balance, base_balance_hold)
        
        # Update quote balance
        quote_balance, quote_balance_hold = self._account.get_asset_balance(quote)
        new_quote_balance = self._account.round_quote(symbol, quote_balance - price * amount)
        if new_quote_balance < 0:
            raise ValueError(f'{symbol} Insufficient balance for {quote} to buy {base}.')
        self._account.update_asset_balance(quote, new_quote_balance, quote_balance_hold)

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
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Update base balance
        base_balance, base_balance_hold = self._account.get_asset_balance(base)
        new_base_balance = self._account.round_base(symbol, base_balance - amount)
        if new_base_balance < 0:
            raise ValueError(f'{symbol} Insufficient balance for {base} to sell {amount}.')
        self._account.update_asset_balance(base, new_base_balance, base_balance_hold)

        # Update quote balance
        quote_balance, quote_balance_hold = self._account.get_asset_balance(quote)
        new_quote_balance = self._account.round_quote(symbol, quote_balance + price * amount)
        self._account.update_asset_balance(quote, new_quote_balance, quote_balance_hold)

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
