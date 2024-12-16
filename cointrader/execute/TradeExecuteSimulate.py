# Implement simulate trading execution for backtesting
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from .ExecuteBase import ExecuteBase
from cointrader.order.OrderResult import OrderResult
from cointrader.order.Order import OrderStatus, OrderType, OrderSide, Order
from cointrader.account.AccountBase import AccountBase
from cointrader.trade.TraderConfig import TraderConfig
import uuid

class TraderExecuteSimulate(ExecuteBase):
    def __init__(self, exchange: TraderExchangeBase, account: AccountBase, config: TraderConfig):
        self._orders: dict[str, Order] = {}
        self._exchange = exchange
        self._account = account
        self._config = config
        self._orders = {}

    def account(self) -> AccountBase:
        return self._account

    def market_buy(self, symbol: str, amount: float, current_price: float, current_ts: int) -> OrderResult:
        """
        Simulate placing a market buy order
        """
        amount = self._account.round_base(symbol, amount)
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.FILLED
        result.side = OrderSide.BUY
        result.type = OrderType.MARKET
        result.price = current_price
        result.size = amount
        result.filled_size = result.size
        result.filled_ts = current_ts

        if self._config.verbose():
            print(f'market_buy: {symbol}, {current_price}, {result.size}')

        if amount < self._account.get_base_min_size(symbol):
            raise ValueError(f'{symbol} Amount is less than the minimum size of {self._account.get_base_min_size(symbol)}')

        # simulate account update
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Update base balance
        base_balance, base_balance_hold = self._account.get_asset_balance(base)
        new_base_balance =  base_balance + amount
        self._account.update_asset_balance(base, new_base_balance, base_balance_hold)
        
        # Update quote balance
        quote_balance, quote_balance_hold = self._account.get_asset_balance(quote)
        new_quote_balance = quote_balance - self._account.round_quote(symbol, current_price * amount)
        if new_quote_balance < 0:
            if self._config.verbose():
                print(f'quote_balance: {quote_balance}, quote_balance_hold: {quote_balance_hold}, new_quote_balance: {new_quote_balance}')
            raise ValueError(f'{symbol} Insufficient balance for {quote} to buy {base}.')
        self._account.update_asset_balance(quote, new_quote_balance, quote_balance_hold)

        self._orders[result.id] = result
        return result

    def market_sell(self, symbol: str, amount: float, current_price: float, current_ts: int) -> OrderResult:
        """
        Simulate placing a market sell order
        """
        amount = self._account.round_base(symbol, amount)
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.FILLED
        result.side = OrderSide.SELL
        result.type = OrderType.MARKET
        result.price = current_price
        result.size = amount
        result.filled_size = result.size
        result.filled_ts = current_ts

        if self._config.verbose():
            print(f'market_sell: {symbol}, {current_price}, {result.size}')

        if amount < self._account.get_base_min_size(symbol):
            raise ValueError(f'{symbol} Amount is less than the minimum size of {self._account.get_base_min_size(symbol)}')

        # simulate account update
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Update base balance
        base_balance, base_balance_hold = self._account.get_asset_balance(base)
        new_base_balance = base_balance - amount
        if new_base_balance < 0:
            if self._config.verbose():
                print(f'base_balance: {base_balance}, new_base_balance: {new_base_balance}')
            raise ValueError(f'{symbol} Insufficient balance for {base} to sell {amount}.')
        self._account.update_asset_balance(base, new_base_balance, base_balance_hold)

        # Update quote balance
        quote_balance, quote_balance_hold = self._account.get_asset_balance(quote)
        new_quote_balance = quote_balance + self._account.round_quote(symbol, current_price * amount)
        self._account.update_asset_balance(quote, new_quote_balance, quote_balance_hold)

        self._orders[result.id] = result
        return result
    
    # Simulate account for limit buy order placed
    def _limit_buy_placed(self, symbol: str, price: float, amount: float):
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)
        quote_balance, quote_hold = self._account.get_asset_balance(quote)
        quote_amount = self._account.round_quote(symbol, price * amount)
        new_quote_balance = quote_balance - quote_amount
        new_quote_hold = quote_hold + quote_amount
        self._account.update_asset_balance(quote, new_quote_balance, new_quote_hold)

        if new_quote_balance < 0:
            if self._config.verbose():
                print(f'quote_balance: {quote_balance}, new_quote_balance: {new_quote_balance}')
            raise ValueError(f'{symbol} Insufficient balance for {quote} to buy {base}.')

    # Simulate account for limit sell order placed
    def _limit_sell_placed(self, symbol: str, price: float, amount: float):
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)
        base_balance, base_hold = self._account.get_asset_balance(base)
        new_base_balance = base_balance - amount
        new_base_hold = base_hold + amount
        self._account.update_asset_balance(base, new_base_balance, new_base_hold)

        if new_base_balance < 0:
            if self._config.verbose():
                print(f'base_balance: {base_balance}, new_base_balance: {new_base_balance}')
            raise ValueError(f'{symbol} Insufficient balance for {base} to sell {amount}.')
    
    def _limit_buy_filled(self, symbol: str, price: float, amount: float):
        """
        Simulate account for limit buy order filled
        """
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Quote hold amount removed
        quote_balance, quote_hold = self._account.get_asset_balance(quote)
        quote_amount = self._account.round_quote(symbol, price * amount)
        new_quote_hold = quote_hold - quote_amount
        self._account.update_asset_balance(quote, quote_balance, new_quote_hold)

        if new_quote_hold < 0:
            if self._config.verbose():
                print(f'quote_balance: {quote_balance}, quote_balance_hold: {quote_hold}, new_quote_hold: {new_quote_hold}')
            raise ValueError(f'{symbol} Insufficient balance for {quote} to buy {base}.')

        # Base balance added
        base_balance, base_hold = self._account.get_asset_balance(base)
        new_base_balance = base_balance + amount
        self._account.update_asset_balance(base, new_base_balance, base_hold)

    def _limit_sell_filled(self, symbol: str, price: float, amount: float):
        """
        Simulate account for limit sell order filled
        """
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Base hold amount removed
        base_balance, base_hold = self._account.get_asset_balance(base)
        new_base_hold = base_hold - amount
        self._account.update_asset_balance(base, base_balance, new_base_hold)

        if new_base_hold < 0:
            if self._config.verbose():
                print(f'base_balance: {base_balance}, base_hold: {base_hold}, new_base_hold: {new_base_hold}')
            raise ValueError(f'{symbol} Insufficient balance for {base} to sell {amount}.')

        # Quote balance added
        quote_balance, quote_hold = self._account.get_asset_balance(quote)
        quote_amount = self._account.round_quote(symbol, price * amount)
        new_quote_balance = quote_balance + quote_amount
        self._account.update_asset_balance(quote, new_quote_balance, quote_hold)

    def _limit_buy_cancelled(self, symbol: str, price: float, amount: float):
        """
        Simulate account for limit buy order cancelled
        """
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Quote hold amount removed
        quote_balance, quote_hold = self._account.get_asset_balance(quote)
        quote_amount = self._account.round_quote(symbol, price * amount)
        new_quote_hold = quote_hold - quote_amount
        new_quote_balance = quote_balance + quote_amount
        self._account.update_asset_balance(quote, new_quote_balance, new_quote_hold)

        if new_quote_hold < 0:
            if self._config.verbose():
                print(f'quote_balance: {quote_balance}, quote_balance_hold: {quote_hold}, new_quote_hold: {new_quote_hold}')
            raise ValueError(f'{symbol} Insufficient balance for {quote} to buy {base}.')

    def _limit_sell_cancelled(self, symbol: str, price: float, amount: float):
        """
        Simulate account for limit sell order cancelled
        """
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Base hold amount removed
        base_balance, base_hold = self._account.get_asset_balance(base)
        new_base_hold = base_hold - amount
        new_base_balance = base_balance + amount
        self._account.update_asset_balance(base, new_base_balance, new_base_hold)

        if new_base_hold < 0:
            if self._config.verbose():
                print(f'base_balance: {base_balance}, base_hold: {base_hold}, new_base_hold: {new_base_hold}')
            raise ValueError(f'{symbol} Insufficient balance for {base} to sell {amount}.')


    def limit_buy(self, symbol: str, limit_price: float, amount: float) -> OrderResult:
        """
        Simulate placing a limit buy order
        """
        amount = self._account.round_base(symbol, amount)
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.BUY
        result.type = OrderType.LIMIT
        result.limit_price = limit_price
        result.size = amount
        result.filled_size = 0.0

        # simulate account update
        self._limit_buy_placed(symbol, limit_price, result.size)

        self._orders[result.id] = result
        return result

    def limit_sell(self, symbol: str, limit_price: float, amount: float) -> OrderResult:
        """
        Simulate placing a limit sell order
        """
        amount = self._account.round_base(symbol, amount)
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.SELL
        result.type = OrderType.LIMIT
        result.limit_price = limit_price
        result.size = amount
        result.filled_size = 0.0

        # simulate account update
        self._limit_sell_placed(symbol, limit_price, result.size)

        self._orders[result.id] = result
        return result

    def stop_loss_limit_buy(self, symbol: str, limit_price: float, stop_price: float, amount: float) -> OrderResult:
        """
        Simulate a stop loss buy order
        """
        amount = self._account.round_base(symbol, amount)
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.BUY
        result.type = OrderType.STOP_LOSS_LIMIT
        result.limit_price = limit_price
        result.stop_price = stop_price
        result.size = amount
        result.filled_size = 0.0

        if self._config.verbose():
            print(f'stop_loss_limit_buy: {symbol}, {limit_price}, {result.size}')

        # simulate account update
        self._limit_buy_placed(symbol, limit_price, result.size)

        self._orders[result.id] = result
        return result

    def stop_loss_limit_sell(self, symbol: str, limit_price: float, stop_price: float, amount: float) -> OrderResult:
        """
        Simulate placing a stop loss sell order
        """
        amount = self._account.round_base(symbol, amount)
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.SELL
        result.type = OrderType.STOP_LOSS_LIMIT
        result.limit_price = limit_price
        result.stop_price = stop_price
        result.size = amount
        result.filled_size = 0.0

        if self._config.verbose():
            print(f'stop_loss_limit_sell: {symbol}, {limit_price}, {amount}, {result.size}')

        # simulate account update
        self._limit_sell_placed(symbol, limit_price, result.size)

        self._orders[result.id] = result
        return result

    def status(self, symbol: str, order_id: str, current_price: float, current_ts: int) -> OrderResult:
        """
        Simulate getting the status of an order
        """
        order = self._orders[order_id]

        bought = False
        sold = False
        if order.type == OrderType.MARKET or order.status == OrderStatus.FILLED:
            return order
        elif order.type == OrderType.LIMIT and order.status == OrderStatus.PLACED:
            if order.side == OrderSide.SELL and current_price >= order.limit_price:
                order.status = OrderStatus.FILLED
                order.price = order.limit_price
                order.filled_size = order.size
                order.filled_ts = current_ts
                sold  = True
            elif order.side == OrderSide.BUY and current_price <= order.limit_price:
                order.status = OrderStatus.FILLED
                order.price = order.limit_price
                order.filled_size = order.size
                order.filled_ts = current_ts
                bought = True
        elif order.type == OrderType.STOP_LOSS_LIMIT and order.status == OrderStatus.PLACED:
            if order.side == OrderSide.SELL and current_price <= order.limit_price:
                order.status = OrderStatus.FILLED
                order.price = order.limit_price
                order.filled_size = order.size
                order.filled_ts = current_ts
                sold = True
            elif order.side == OrderSide.BUY and current_price >= order.limit_price:
                order.status = OrderStatus.FILLED
                order.price = order.limit_price
                order.filled_size = order.size
                order.filled_ts = current_ts
                bought = True

        # if the buy was executed, then update the account, transfer base hold to balance
        # if the sell was executed, then update the account, transfer quote hold to balance
        if bought:
            self._limit_buy_filled(symbol, order.limit_price, order.size)
        if sold:
            self._limit_sell_filled(symbol, order.limit_price, order.size)
        return order

    def cancel(self, symbol: str, order_id: str, current_price: float, current_ts: int) -> OrderResult:
        """
        Simulate cancelling an order
        """
        order = self._orders[order_id]

        if self._config.verbose():
            print(f'cancel: {symbol}, {order_id}, {current_price}')

        if order.type == OrderType.MARKET or order.status == OrderStatus.CANCELLED or order.status == OrderStatus.FILLED:
            return order

        cancel_buy = False
        cancel_sell = False

        if order.type == OrderType.LIMIT and order.status == OrderStatus.PLACED:
            if order.side == OrderSide.SELL:
                if current_price < order.limit_price:
                    order.status = OrderStatus.CANCELLED
                    cancel_sell = True
            elif order.side == OrderSide.BUY:
                if current_price > order.limit_price:
                    order.status = OrderStatus.CANCELLED
                    cancel_buy = True
        elif order.type == OrderType.STOP_LOSS_LIMIT and order.status == OrderStatus.PLACED:
            if order.side == OrderSide.SELL:
                if current_price > order.limit_price:
                    order.status = OrderStatus.CANCELLED
                    cancel_sell = True
            elif order.side == OrderSide.BUY:
                if current_price < order.limit_price:
                    order.status = OrderStatus.CANCELLED
                    cancel_buy = True

        # if the cancelled buy was executed, then update the account, transfer quote hold to quote balance
        # if the cancelled sell was executed, then update the account, transfer base hold to base balance
        if order.status == OrderStatus.CANCELLED:           
            if cancel_buy:
                # simulate account update
                self._limit_buy_cancelled(symbol, order.limit_price, order.size)

            if cancel_sell:
                # simulate account update
                self._limit_sell_cancelled(symbol, order.limit_price, order.size)

        return order
