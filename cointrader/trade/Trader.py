# Using market and account info, creates TraderPosition for a given symbol when entered into a position
# Trader only operates on a designated symbol
from cointrader.common.Kline import Kline
from cointrader.common.Strategy import Strategy
from cointrader.common.LogLevel import LogLevel
from cointrader.account.Account import Account
from .TraderConfig import TraderConfig
from cointrader.execute.ExecuteBase import ExecuteBase
from cointrader.execute.pipeline.ExecutePipeline import ExecutePipeline
from .position.TraderPosition import TraderPosition
from cointrader.order.Orders import Orders
from cointrader.order.OrderRequest import OrderRequest
from cointrader.order.enum.OrderType import OrderType
from cointrader.order.enum.OrderStatus import OrderStatus
from cointrader.order.enum.OrderSide import OrderSide
from cointrader.common.TradeLossBase import TradeLossBase
from cointrader.common.TradeSizeBase import TradeSizeBase
import importlib
from colorama import Fore, Back, Style
import time
from datetime import datetime

class Trader(object):
    _symbol = None
    _account: Account = None
    _exec_pipe: ExecutePipeline = None
    _positions: list[TraderPosition] = []
    _strategy_name = None
    _strategy: Strategy = None
    _long_strategy: Strategy = None
    _loss_strategy: TradeLossBase = None
    _size_strategy: TradeSizeBase = None
    _orders: Orders = None
    _max_positions_per_symbol = 0

    def __init__(self, account: Account, symbol: str, exec_pipe: ExecutePipeline, config: TraderConfig, orders: Orders, granularity: int = 0, strategy_weights: dict[str, float] = None):
        self._symbol = symbol
        self._account = account
        self._execute = exec_pipe.execute()
        self._exec_pipe = exec_pipe
        self._config = config
        self._orders = orders
        self._granularity = granularity
        self._disabled = False
        self._cur_id = 0
        self._total_position_count = 0
        self._total_closed_positive_position_count = 0
        self._total_closed_negative_position_count = 0
        self._positions = []
        self._buys = []
        self._sells = []
        # configuration for strategies
        self._strategy_weights = strategy_weights
        self._strategies_other_config = config.strategies_other_timeframes()
        self._strategies_other_timeframes: dict[str, Strategy] = {}
        self._strategy_name = config.strategy()

        # load the strategies for each granularity
        for s in self._strategies_other_config:
            strategy_name, strategy_granularity = s.split(':')
            strategy_module = importlib.import_module(f'cointrader.strategies.{strategy_name}')
            self._strategies_other_timeframes[strategy_granularity] = getattr(strategy_module, strategy_name)(symbol=symbol, granularity=int(strategy_granularity), weights=strategy_weights)

        # load the main strategy
        strategy_module = importlib.import_module(f'cointrader.strategies.{self._strategy_name}')
        self._strategy = getattr(strategy_module, self._strategy_name)(symbol=symbol, granularity=granularity, weights=strategy_weights)

        # load the loss and size strategies
        loss_module = importlib.import_module(f'cointrader.trade.loss.{self._config.loss_strategy()}')
        self._loss_strategy = getattr(loss_module, self._config.loss_strategy())(symbol=symbol, account=account, config=config)
        size_module = importlib.import_module(f'cointrader.trade.size.{self._config.size_strategy()}')
        self._size_strategy = getattr(size_module, self._config.size_strategy())(symbol=symbol, account=account, config=config)

        self._max_positions_per_symbol = config.max_positions_per_symbol()

        # control disabling new positions from this specific trader (disabled by default)
        self._local_disable_new_positions = True
        self._prev_local_disable_new_positions = True
        self._global_prev_disable_new_positions = False

        self._net_profit_percent = 0.0
        self._positive_profit_percent = 0.0
        self._negative_profit_percent = 0.0
        self._stop_loss_percent = config.stop_loss_percent()
        self._cooldown_period_seconds = config.cooldown_period_seconds()
        self._disable_after_loss_seconds = config.disable_after_loss_seconds()
        self._disable_until_ts = 0

        #print(f'{self._symbol} Loading strategy: {self._strategy_name} max_positions={self._max_positions_per_symbol}')


    def symbol(self) -> str:
        return self._symbol
    

    def position_count(self) -> int:
        """
        Get the number of positions open
        """
        return len(self._positions)
    

    # def disable_new_positions(self, disable: bool):
    #     """
    #     Disable opening new positions
    #     """
    #     self._local_disable_new_positions = disable

    
    def restore_positions(self, current_price: float, current_ts: int) -> bool:
        """
        Restore positions from the database. Used if trading bot exits prematurely, and we need to restore the positions from the order database
        """
        orders = self._orders.get_active_orders(symbol=self._symbol)
        order_by_pid = {}
        # reorganize orders by pid
        for order in orders:
            # if the order is cancelled, skip it and set inactive
            if order.cancelled():
                self._orders.update_order_active(symbol=self._symbol, order_id=order.id, active=False)
                continue
            if order.pid not in order_by_pid.keys():
                if order.side == OrderSide.BUY:
                    #result = self._execute.status(order_id=order.id, symbol=self._symbol, current_price=current_price, current_ts=current_ts)
                    oreq = OrderRequest(symbol=self._symbol, type=OrderType.STATUS, current_price=current_price, current_ts=current_ts)
                    oreq.order_id = order.id

                    # TODO: replace with order pipeline
                    result = self._execute.execute_order(oreq)

                    order.update_order(result)
                    if order.placed():
                        # for simplicity, just cancel the open order
                        if self._config.log_level() >= LogLevel.INFO.value:
                            print(f"{self._symbol} Cancelling buy order {order}")
                        #result = self._execute.cancel(order_id=order.id, symbol=self._symbol, current_price=current_price, current_ts=current_ts)
                        oreq = OrderRequest(symbol=self._symbol, type=OrderType.CANCEL, current_price=current_price, current_ts=current_ts)
                        oreq.order_id = order.id

                        # TODO: replace with order pipeline
                        result = self._execute.execute_order(oreq)

                        if not self._config.simulate():
                            time.sleep(1)
                        order.update_order(result)
                        order.active = False
                        self._orders.update_order(symbol=self._symbol, order=order)
                    elif order.filled():
                        order_by_pid[order.pid] = order

                elif order.side == OrderSide.SELL and order.placed():
                    # to keep things simple, just cancel the order
                    if self._config.log_level() >= LogLevel.INFO.value:
                        print(f"{self._symbol} Cancelling sell order {order}")
                    #result = self._execute.cancel(order_id=order.id, symbol=self._symbol, current_price=current_price, current_ts=current_ts)
                    oreq = OrderRequest(symbol=self._symbol, type=OrderType.CANCEL, current_price=current_price, current_ts=current_ts)
                    oreq.order_id = order.id

                    # TODO: replace with order pipeline
                    result = self._execute.execute_order(oreq)

                    if not self._config.simulate():
                        time.sleep(1)
                    order.update_order(result)
                    order.active = False
                    self._orders.update_order(symbol=self._symbol, order=order)
            else:
                if order.side == OrderSide.BUY and order.placed():
                    if self._config.log_level() >= LogLevel.WARNING.value:
                        print(f"Error: Duplicate buy order found, cancelling order: {order}")
                    #result = self._execute.cancel(order_id=order.id, symbol=self._symbol, current_price=current_price, current_ts=current_ts)
                    oreq = OrderRequest(symbol=self._symbol, type=OrderType.CANCEL, current_price=current_price, current_ts=current_ts)
                    oreq.order_id = order.id

                    # TODO: replace with order pipeline
                    result = self._execute.execute_order(oreq)

                    if not self._config.simulate():
                        time.sleep(1)
                    order.update_order(result)
                    order.active = False
                    self._orders.update_order(symbol=self._symbol, order=order)
        
        # restore the positions with buy orders
        for _, order in order_by_pid.items():
            if self._config.log_level() >= LogLevel.INFO.value:
                print(f"{self._symbol} Restoring position from order: {order}")
            position = TraderPosition(symbol=self._symbol, pid=self._cur_id, strategy=self._strategy, exec_pipe=self._exec_pipe, config=self._config, orders=self._orders)
            position.restore_buy_order(order=order, current_price=current_price, current_ts=current_ts)
            self._positions.append(position)
            self._cur_id += 1


    def market_preload(self, klines: list[Kline]):
        """
        Preload klines for the strategy
        """
        for kline in klines:
            self._strategy.update(kline=kline)
            self._loss_strategy.update(kline=kline)
            self._size_strategy.update(kline=kline)


    def market_update_kline_other_timeframe(self, kline: Kline, granularity: int, preload: bool = False):
        """
        Update the strategy for a different timeframe
        """
        if str(granularity) not in self._strategies_other_timeframes.keys():
            if not self._config.simulate():
                print(f"Granularity {granularity} not found in strategies: {self._strategies_other_timeframes.keys()}")
            return

        strategy = self._strategies_other_timeframes[str(granularity)]
        strategy.update(kline)

        # disable opening new positions on a sell signal from another timeframe
        # re-enable opening new positions on a buy signal from another timeframe
        if strategy.buy_signal():
            self._local_disable_new_positions = False
            if not preload and self._prev_local_disable_new_positions != self._local_disable_new_positions:
                if self._config.log_level() >= LogLevel.INFO.value:
                    print(f'{Fore.GREEN}{self._symbol} strategy {strategy.name()} buy signal {self._strategy.buy_signal_name()} granularity={granularity}{Style.RESET_ALL}')
            self._prev_local_disable_new_positions = self._local_disable_new_positions
        
        if strategy.sell_signal():
            self._local_disable_new_positions = True
            if not preload and self._prev_local_disable_new_positions != self._local_disable_new_positions:
                if self._config.log_level() >= LogLevel.INFO.value:
                    print(f'{Fore.RED}{self._symbol} strategy {strategy.name()} sell signal {self._strategy.sell_signal_name()} granularity={granularity}{Style.RESET_ALL}')
            self._prev_local_disable_new_positions = self._local_disable_new_positions

    def market_update_kline(self, kline: Kline, granularity: int):
        """
        Update the strategy for the symbol with the kline
        """
        if not kline:
            return
        if granularity == self._granularity:
            # update the main strategy
            self._strategy.update(kline=kline)
            self._loss_strategy.update(kline=kline)
            self._size_strategy.update(kline=kline)


    def market_update_price(self, current_price: float, current_ts: int, granularity: int = 0):
        """
        Update the market price for the symbol
        """
        # if position has been closed, remove it from the list
        for position in self._positions:
            if granularity == self._granularity:
                position.market_update(current_price=current_price, current_ts=current_ts)

            # handle trailing stop loss, prevent placing stop loss if we have already started closing the position
            if position.opened() and not position.closed_position() and self._config.trailing_stop_loss():
                self.update_trailing_stop_loss_position(position, current_price, current_ts)

            # handle closed position when sell order or stop loss has been filled
            if position.closed():
                # mark the orders as inactive in Orders
                buy_order = position.buy_order()
                if buy_order:
                    self._orders.update_order_active(self._symbol, buy_order.id, False)
                sell_order = position.sell_order()
                if sell_order:
                    self._orders.update_order_active(self._symbol, sell_order.id, False)
                stop_loss_order = position.stop_loss_order()
                if stop_loss_order:
                    self._orders.update_order_active(self._symbol, stop_loss_order.id, False)
                self.remove_position(position, current_ts)

        # Disable opening new positions for a period of time after a loss
        if self._disable_until_ts != 0 and current_ts >= self._disable_until_ts:
            self._disable_until_ts = 0
            self._disabled = False

        opened_position_id = -1
        buy_signal = self._strategy.buy_signal()

        # global disable new positions
        disable_new_positions = self._config.global_disable_new_positions()
        if disable_new_positions != self._global_prev_disable_new_positions and self._config.log_level() >= LogLevel.INFO.value:
            print(f"{self._symbol} global_disable_positions: {disable_new_positions}")
        self._global_prev_disable_new_positions = disable_new_positions

        # check if new positions are locally disabled
        if self._local_disable_new_positions:
            disable_new_positions = True

        # if we configured to only allow opening new positions after buy orders have completed on all open positions,
        # then disable new positions until all buy orders have completed
        if self._config.position_open_buy_complete() and not self.positions_buy_orders_completed():
            disable_new_positions = True

        # Open a position on a buy signal
        if not self._disabled and not disable_new_positions and buy_signal and len(self._positions) < self._max_positions_per_symbol:
            if not self._size_strategy.ready():
                if self._config.log_level() >= LogLevel.WARNING.value:
                    print(f"{self._symbol} Size strategy not ready")
                return
            size = self._size_strategy.get_base_trade_size(current_price=current_price, current_ts=current_ts)
            quote_size = self._size_strategy.get_quote_trade_size(current_price=current_price, current_ts=current_ts)
            if not size or not quote_size:
                if self._config.log_level() >= LogLevel.WARNING.value:
                    print(f"{self._symbol} Size too small: {size}")
                return

            # check if we have sufficient balance to open the position
            quote_name = self._account.get_quote_name(self._symbol)
            #balance, _ = self._account.get_asset_balance(quote_name, round=False)
            balance = self._config.global_current_balance_quote()
            #print("balance", balance, self._config.quote_currency())
            balance = self._account.round_quote(self._symbol, balance)
            if balance < quote_size:
                # prevent spamming the console with insufficient balance messages in live trading
                if self._config.simulate() and self._config.log_level() >= LogLevel.WARNING.value:
                    print(f"{self._symbol} {quote_name} Insufficient balance {balance} to open position at price {current_price} quote_size={quote_size}")
                return

            if not self._config.simulate():
                print(f"{self._symbol} Buy signal {self._strategy.buy_signal_name()} for {self._symbol} size={size}")

            #print(f'Buy signal {self._strategy.buy_signal_name()} for {self._symbol}')
            position = TraderPosition(symbol=self._symbol, pid=self._cur_id, strategy=self._strategy, exec_pipe=self._exec_pipe, config=self._config, orders=self._orders)
            if position.open_position(size=size, current_price=current_price, current_ts=current_ts):
                # if position successfully opened, update quote balance
                self._config.set_global_current_balance_quote(balance - quote_size)
                self._total_position_count += 1
                opened_position_id = self._cur_id
                self._positions.append(position)
                self._cur_id += 1
                if self._cooldown_period_seconds > 0:
                    self._disabled = True
                    self._disable_until_ts = current_ts + self._cooldown_period_seconds

                # if we have a market order filled immediately, then set the stop loss
                if position.opened() and self._config.trailing_stop_loss() and self._loss_strategy.ready():
                    stop_price = self._loss_strategy.get_stop_loss_price(price=position.buy_price(), current_ts=current_ts)
                    stop_limit_price = self._loss_strategy.get_stop_limit_price(price=position.buy_price(), current_ts=current_ts)
                    if self._config.log_level() >= LogLevel.INFO.value:
                        print(f"{self._symbol} Stop loss: {stop_price} Limit: {stop_limit_price}")

                    # handle setting and updating stop loss orders if enabled
                    if not position.stop_loss_is_set():
                        #print(f"buy price: {position.buy_price()} Stop price: {stop_price}")
                        position.create_stop_loss_position(stop_price=stop_price, limit_price=stop_limit_price, current_ts=current_ts)

        strategy_sell_signal = self._strategy.sell_signal()

        # Try to close position(s) on a sell signal
        if len(self._positions) > 0:
            for position in self._positions:
                # for a position that hasn't completed the buy order yet, skip it
                if position.pid() == opened_position_id:
                    continue

                # for limit and stop loss orders, we may need to cancel them if the price has moved, and place a new order
                if not self._disabled and buy_signal:
                    if not self._size_strategy.ready():
                        continue
                    size = self._size_strategy.get_base_trade_size(current_price=current_price, current_ts=current_ts)
                    quote_size = self._size_strategy.get_quote_trade_size(current_price=current_price, current_ts=current_ts)
                    if not quote_size:
                        continue

                    # check if we have sufficient balance to update the buy position
                    quote_name = self._account.get_quote_name(self._symbol)
                    #balance, _ = self._account.get_asset_balance(quote_name, round=False)
                    balance = self._config.global_current_balance_quote()
                    #print("balance", balance, self._config.quote_currency())
                    balance = self._account.round_quote(self._symbol, balance)
                    if balance >= quote_size:
                        position.update_buy_position(size=size, current_price=current_price, current_ts=current_ts)
                    elif self._config.log_level() >= LogLevel.WARNING.value:
                        print(f"{self._symbol} {quote_name} Insufficient balance {balance} (quote_size={quote_size}) to update buy position at price {current_price}")

                # skip checking for sell signal if position has not been opened
                if not position.opened():
                    continue

                sell_signal = False
                sell_signal_name = None
                if strategy_sell_signal:
                    # Only sell if we have met the minimum take profit percent
                    if self._config.min_take_profit_percent() <= position.current_position_percent(current_price):
                        sell_signal = True
                        sell_signal_name = self._strategy.sell_signal_name()
                # if we have not yet attempted to close the position
                if sell_signal:
                    if not self._config.simulate():
                        print(f'Sell signal {sell_signal_name} for {self._symbol} {position.pid()}')
                    if not position.closed_position():
                        #print(f'Sell signal {sell_signal_name} for {self._symbol}')
                        #base_name = self._account.get_base_name(self._symbol)
                        #balance, _ = self._account.get_asset_balance(base_name, round=False)
                        #if not position.stop_loss_is_set() and balance < position.buy_size():
                        #    print(f"{self._symbol} {base_name} Insufficient balance {balance} to close position at price {current_price}")
                        #else:
                        position.close_position(current_price=current_price, current_ts=current_ts)
                    elif not position.closed():
                        # for limit and stop loss orders, we may need to cancel them if the price has moved, and place a new order
                        #base_name = self._account.get_base_name(self._symbol)
                        #balance, _ = self._account.get_asset_balance(base_name, round=True)
                        #if not position.stop_loss_is_set() and balance < position.buy_size():
                        #    print(f"{self._symbol} {base_name} Insufficient balance {balance} to update sell position at price {current_price}")
                        #else:
                        position.update_sell_position(current_price=current_price, current_ts=current_ts)


    def positions_buy_orders_completed(self):
        """
        Check if all buy orders have been completed for all open positions
        """
        for position in self._positions:
            if not position.buy_order_completed():
                return False
        return True


    def update_trailing_stop_loss_position(self, position: TraderPosition, current_price: float, current_ts: int):
        """
        Update the trailing stop loss position
        """
        # check if we have already closed the position, then we can't create a stop loss order
        if position.closed():
            return
        
        if not self._loss_strategy.ready():
            return

        percent = self._config.stop_loss_percent()
        # set the stop X% above the limit price
        stop_price = self._loss_strategy.get_stop_loss_price(price=position.buy_price(), current_ts=current_ts)
        stop_limit_price = self._loss_strategy.get_stop_limit_price(price=position.buy_price(), current_ts=current_ts)
        # handle setting and updating stop loss orders if enabled
        if not position.stop_loss_is_set():
            # check if we have sufficient balance to create the stop loss order
            base_name = self._account.get_base_name(self._symbol)
            balance, _ = self._account.get_asset_balance(base_name, round=False)
            balance = self._account.round_base(self._symbol, balance)
            if balance < position.buy_size():
                print(f"{self._symbol} {base_name} Insufficient balance {balance} to create stop loss position at price {current_price}")
                return
            #print(f"buy price: {position.buy_price()} Stop price: {stop_price}")
            position.create_stop_loss_position(stop_price=stop_price, limit_price=stop_limit_price, current_ts=current_ts)
        else:
            # update the stop loss order so it trails the position, if the price has moved up 1%
            stop_loss_limit_price = position.stop_loss_limit_price()
            if ((current_price - stop_loss_limit_price) / stop_loss_limit_price) * 100.0 > percent + 1.0:
                position.cancel_stop_loss_position()
                if not self._config.simulate():
                    # wait for the order to be cancelled
                    time.sleep(1)

                # check if we have sufficient balance to update the stop loss order
                base_name = self._account.get_base_name(self._symbol)
                balance, _ = self._account.get_asset_balance(base_name, round=False)
                balance = self._account.round_base(self._symbol, balance)
                if balance < position.buy_size():
                    print(f"{self._symbol} {base_name} Insufficient balance {balance} to update stop loss position at price {current_price}")
                    return
                #new_stop_price = self._account.round_quote(self._symbol, (1 - ((percent - stop_loss_limit_percent) / 100.0)) * current_price)
                #new_stop_limit_price = self._account.round_quote(self._symbol, (1 - (percent / 100.0)) * current_price)
                new_stop_price = self._loss_strategy.get_stop_loss_price(price=current_price, current_ts=current_ts)
                new_stop_limit_price = self._loss_strategy.get_stop_limit_price(price=current_price, current_ts=current_ts)
                #print(f"{self._symbol} Updating stop loss: {stop_loss_limit_price} -> {new_stop_limit_price}")
                position.create_stop_loss_position(stop_price=new_stop_price, limit_price=new_stop_limit_price, current_ts=current_ts)


    def remove_position(self, position: TraderPosition, current_ts: int):
        """
        Remove a position from the list, and collect stats on the position
        """
        profit_percent = position.profit_percent()
        buy_price = position.buy_price()
        sell_price = position.sell_price()
        buy_date = datetime.fromtimestamp(position.buy_ts())
        sell_date = datetime.fromtimestamp(position.sell_ts())
        self._config.set_global_last_closed_position_profit(profit=profit_percent)
        if profit_percent >= 0:
            self._positive_profit_percent += profit_percent
            self._total_closed_positive_position_count += 1
            if self._config.log_level() >= LogLevel.INFO.value:
                msg = f"{Fore.GREEN}{self._symbol} Profit: {position.profit_percent()}"
                msg += f" Buy: {buy_price} Sell: {sell_price} Buy Date: {buy_date} Sell Date: {sell_date}"
                msg += f"{Style.RESET_ALL}"
                print(msg)
        else:
            self._negative_profit_percent += profit_percent
            self._total_closed_negative_position_count += 1
            if self._config.log_level() >= LogLevel.INFO.value:
                msg = f"{Fore.RED}{self._symbol} Profit: {position.profit_percent()}"
                msg += f" Buy: {buy_price} Sell: {sell_price} Buy Date: {buy_date} Sell Date: {sell_date}"
                msg += f"{Style.RESET_ALL}"
                print(msg)
            # Disable opening new positions for a period of time after a loss
            if self._disable_after_loss_seconds > 0:
                self._disable_until_ts = current_ts + self._disable_after_loss_seconds
                self._disabled = True

        self._net_profit_percent += profit_percent

        if self._config.simulate():
            self._buys.append(position.buy_info())
            self._sells.append(position.sell_info())
        self._positions.remove(position)


    def net_profit_percent(self) -> float:
        """
        Get the net profit percent for the symbol
        """
        return self._net_profit_percent


    def positive_profit_percent(self) -> float:
        """
        Get the positive profit percent for the symbol
        """
        return self._positive_profit_percent


    def negative_profit_percent(self) -> float:
        """
        Get the negative profit percent for the symbol
        """
        return self._negative_profit_percent


    def positive_profit_closed_position_count(self) -> int:
        """
        Get the total number of closed positive positions
        """
        return self._total_closed_positive_position_count


    def negative_profit_closed_position_count(self) -> int:
        """
        Get the total number of closed negative positions
        """
        return self._total_closed_negative_position_count


    def positive_average_profit_percent(self) -> float:
        """
        Get the average positive profit percent for the symbol
        """
        if self._total_closed_positive_position_count == 0:
            return 0
        return self._positive_profit_percent / self._total_closed_positive_position_count

    def negative_average_profit_percent(self) -> float:
        """
        Get the average negative profit percent for the symbol
        """
        if self._total_closed_positive_position_count == 0:
            return 0
        return self._negative_profit_percent / self._total_closed_negative_position_count

    def buys(self) -> list:
        """
        Get the list of all buy orders for the symbol (for simulation)
        """
        return self._buys
    

    def sells(self) -> list:
        """
        Get the list of all sell orders for the symbol (for simulation)
        """
        return self._sells

    def total_position_count(self) -> int:
        """
        Get the total number of positions opened
        """
        return self._total_position_count
