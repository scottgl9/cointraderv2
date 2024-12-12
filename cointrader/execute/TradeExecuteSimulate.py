# Implement simulate trading execution for backtesting
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from .ExecuteBase import ExecuteBase
from cointrader.order.OrderResult import OrderResult
from cointrader.order.Order import OrderStatus, OrderType, OrderSide
from cointrader.account.AccountBase import AccountBase
from cointrader.trade.TraderConfig import TraderConfig
import uuid

class TraderExecuteSimulate(ExecuteBase):
    def __init__(self, exchange: TraderExchangeBase, account: AccountBase, config: TraderConfig):
        self._exchange = exchange
        self._account = account
        self._config = config
        self._orders = {}

    def account(self) -> AccountBase:
        return self._account

    def market_buy(self, symbol: str, price: float, amount: float) -> OrderResult:
        """
        Simulate placing a market buy order
        """
        if self._config.verbose():
            print(f'market_buy: {symbol}, {price}, {amount}')
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.FILLED
        result.side = OrderSide.BUY
        result.type = OrderType.MARKET
        result.price = price
        result.size = self._account.round_base(symbol, amount)
        result.filled_size = result.size

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
        new_quote_balance = quote_balance - self._account.round_quote(symbol, price * amount)
        if new_quote_balance < 0:
            if self._config.verbose():
                print(f'quote_balance: {quote_balance}, quote_balance_hold: {quote_balance_hold}, new_quote_balance: {new_quote_balance}')
            raise ValueError(f'{symbol} Insufficient balance for {quote} to buy {base}.')
        self._account.update_asset_balance(quote, new_quote_balance, quote_balance_hold)

        self._orders[result.id] = result
        return result

    def market_sell(self, symbol: str, price: float, amount: float) -> OrderResult:
        """
        Simulate placing a market sell order
        """
        if self._config.verbose():
            print(f'market_sell: {symbol}, {price}, {amount}')
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.FILLED
        result.side = OrderSide.SELL
        result.type = OrderType.MARKET
        result.price = price
        result.size = self._account.round_base(symbol, amount)
        result.filled_size = result.size

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
        new_quote_balance = quote_balance + self._account.round_quote(symbol, price * amount)
        self._account.update_asset_balance(quote, new_quote_balance, quote_balance_hold)

        self._orders[result.id] = result
        return result
    
    def limit_buy(self, symbol: str, price: float, amount: float) -> OrderResult:
        """
        Simulate placing a limit buy order
        """
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.BUY
        result.type = OrderType.LIMIT
        result.price = price
        result.size = self._account.round_base(symbol, amount)
        result.filled_size = 0.0

        # simulate account update
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Update base hold amount
        base_balance, base_hold = self._account.get_asset_balance(base)
        new_base_hold = base_hold + amount
        self._account.update_asset_balance(base, base_balance, new_base_hold)

        # Update quote hold amount
        quote_balance, quote_hold = self._account.get_asset_balance(quote)
        new_quote_hold = quote_hold - self._account.round_quote(symbol, price * amount)
        self._account.update_asset_balance(quote, quote_balance, new_quote_hold)

        self._orders[result.id] = result
        return result

    def limit_sell(self, symbol: str, price: float, amount: float) -> OrderResult:
        """
        Simulate placing a limit sell order
        """
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.SELL
        result.type = OrderType.LIMIT
        result.price = price
        result.size = self._account.round_base(symbol, amount)
        result.filled_size = 0.0

        # simulate account update
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Update base hold amount
        base_balance, base_hold = self._account.get_asset_balance(base)
        new_base_hold = base_hold - amount
        self._account.update_asset_balance(base, base_balance, new_base_hold)

        # Update quote hold amount
        quote_balance, quote_hold = self._account.get_asset_balance(quote)
        new_quote_hold = quote_hold + self._account.round_quote(symbol, price * amount)
        self._account.update_asset_balance(quote, quote_balance, new_quote_hold)

        self._orders[result.id] = result
        return result

    def stop_loss_buy(self, symbol: str, price: float, stop_price: float, amount: float) -> OrderResult:
        """
        Simulate a stop loss buy order
        """
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.BUY
        result.type = OrderType.STOP_LOSS_LIMIT
        result.price = price
        result.limit_price = stop_price
        result.size = self._account.round_base(symbol, amount)
        result.filled_size = 0.0

        # simulate account update
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Update base hold amount
        base_balance, base_hold = self._account.get_asset_balance(base)
        new_base_hold = base_hold + amount
        self._account.update_asset_balance(base, base_balance, new_base_hold)

        # Update quote hold amount
        quote_balance, quote_hold = self._account.get_asset_balance(quote)
        new_quote_hold = quote_hold - self._account.round_quote(symbol, price * amount)
        self._account.update_asset_balance(quote, quote_balance, new_quote_hold)

        self._orders[result.id] = result
        return result

    def stop_loss_sell(self, symbol: str, price: float, stop_price: float, amount: float) -> OrderResult:
        """
        Simulate placing a stop loss sell order
        """
        result = OrderResult(symbol)
        result.id = str(uuid.uuid4())
        result.status = OrderStatus.PLACED
        result.side = OrderSide.SELL
        result.type = OrderType.STOP_LOSS_LIMIT
        result.price = price
        result.limit_price = stop_price
        result.size = self._account.round_base(symbol, amount)
        result.filled_size = 0.0

        # simulate account update
        base = self._exchange.info_ticker_get_base(symbol)
        quote = self._exchange.info_ticker_get_quote(symbol)

        # Update base hold amount
        base_balance, base_hold = self._account.get_asset_balance(base)
        new_base_hold = base_hold - amount
        self._account.update_asset_balance(base, base_balance, new_base_hold)

        # Update quote hold amount
        quote_balance, quote_hold = self._account.get_asset_balance(quote)
        new_quote_hold = quote_hold + self._account.round_quote(symbol, price * amount)
        self._account.update_asset_balance(quote, quote_balance, new_quote_hold)

        self._orders[result.id] = result
        return result

    def status(self, symbol: str, order_id: str, price: float) -> OrderResult:
        """
        Simulate getting the status of an order
        """
        for order in self._orders:
            if order.id != order_id:
                continue

            bought = False
            sold = False
            if order.type == OrderType.MARKET:
                return self._orders[order]
            elif order.type == OrderType.LIMIT:
                if order.side == OrderSide.SELL and price >= order.price:
                    order.status = OrderStatus.FILLED
                    order.filled_size = order.size
                    sold  = True
                elif order.side == OrderSide.BUY and price <= order.price:
                    order.status = OrderStatus.FILLED
                    order.filled_size = order.size
                    bought = True
            elif order.type == OrderType.STOP_LOSS_LIMIT:
                if order.side == OrderSide.SELL and price <= order.limit_price:
                    order.status = OrderStatus.FILLED
                    order.filled_size = order.size
                    sold = True
                elif order.side == OrderSide.BUY and price >= order.limit_price:
                    order.status = OrderStatus.FILLED
                    order.filled_size = order.size
                    bought = True
            
            # if the buy was executed, then update the account, transfer base hold to balance
            # if the sell was executed, then update the account, transfer quote hold to balance
            if bought:
                base = self._exchange.info_ticker_get_base(symbol)
                base_balance, base_hold = self._account.get_asset_balance(base)
                new_base_hold = base_hold - order.size
                new_base_balance = base_balance + order.size
                self._account.update_asset_balance(base, new_base_balance, new_base_hold)
            if sold:
                quote = self._exchange.info_ticker_get_quote(symbol)
                quote_balance, quote_hold = self._account.get_asset_balance(quote)
                amount = self._account.round_quote(symbol, price * order.size)
                new_quote_hold = quote_hold - amount
                new_quote_balance = quote_balance + amount
                self._account.update_asset_balance(quote, new_quote_balance, new_quote_hold)

            return order
        return None

    def cancel(self, symbol: str, order_id: str, price: float) -> OrderResult:
        """
        Simulate cancelling an order
        """
        for order in self._orders:
            if order.id != order_id:
                continue
            if order.type == OrderType.MARKET:
                continue

            bought = False
            sold = False

            if order.type == OrderType.LIMIT:
                if order.side == OrderSide.SELL:
                    # check if the sell order has already executed
                    if price < order.price:
                        order.status = OrderStatus.CANCELLED
                    else:
                        order.status = OrderStatus.FILLED
                        order.filled_size = order.size
                    sold = True
                elif order.side == OrderSide.BUY:
                    # check if the buy order has already executed
                    if price > order.price:
                        order.status = OrderStatus.CANCELLED
                    else:
                        order.status = OrderStatus.FILLED
                        order.filled_size = order.size
                    bought = True
            elif order.type == OrderType.STOP_LOSS_LIMIT:
                if order.side == OrderSide.SELL:
                    # check if the sell order has already executed
                    if price > order.limit_price:
                        order.status = OrderStatus.CANCELLED
                    else:
                        order.status = OrderStatus.FILLED
                        order.filled_size = order.size
                    sold = True
                elif order.side == OrderSide.BUY:
                    # check if the buy order has already executed
                    if price < order.limit_price:
                        order.status = OrderStatus.CANCELLED
                    else:
                        order.status = OrderStatus.FILLED
                        order.filled_size = order.size
                    sold = True
                
                # if the cancelled buy was executed, then update the account, transfer base hold to balance
                # if the cancelled sell was executed, then update the account, transfer quote hold to balance
                # *TODO* implement account balance transfers
                if order.status == OrderStatus.CANCELLED:
                    amount = order.size
                    
                    if bought:
                        # simulate account update
                        base = self._exchange.info_ticker_get_base(symbol)
                        quote = self._exchange.info_ticker_get_quote(symbol)
                
                        # Update base hold amount
                        base_balance, base_hold = self._account.get_asset_balance(base)
                        new_base_hold = base_hold - amount
                        self._account.update_asset_balance(base, base_balance, new_base_hold)
                
                        # Update quote hold amount
                        quote_balance, quote_hold = self._account.get_asset_balance(quote)
                        new_quote_hold = quote_hold + self._account.round_quote(symbol, price * amount)
                        self._account.update_asset_balance(quote, quote_balance, new_quote_hold)
                    if sold:
                         # simulate account update
                        base = self._exchange.info_ticker_get_base(symbol)
                        quote = self._exchange.info_ticker_get_quote(symbol)
                
                        # Update base hold amount
                        base_balance, base_hold = self._account.get_asset_balance(base)
                        new_base_hold = base_hold + amount
                        self._account.update_asset_balance(base, base_balance, new_base_hold)
                
                        # Update quote hold amount
                        quote_balance, quote_hold = self._account.get_asset_balance(quote)
                        new_quote_hold = quote_hold - self._account.round_quote(symbol, price * amount)
                        self._account.update_asset_balance(quote, quote_balance, new_quote_hold)

                return order
        return None
