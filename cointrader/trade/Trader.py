# Using market and account info, creates TraderPosition for a given symbol when entered into a position
# Trader only operates on a designated symbol
from cointrader.common.Kline import Kline
from cointrader.common.Strategy import Strategy
from cointrader.account.Account import Account
from .TraderConfig import TraderConfig
from cointrader.execute.ExecuteBase import ExecuteBase
from .TraderPosition import TraderPosition
from cointrader.order.Orders import Orders
import importlib
from colorama import Fore, Back, Style

class Trader(object):
    _symbol = None
    _account = None
    _positions = []
    _strategy_name = None
    _strategy = None
    _max_positions = 0

    def __init__(self, account: Account, symbol: str, execute: ExecuteBase, config: TraderConfig, orders: Orders):
        self._symbol = symbol
        self._account = account
        self._execute = execute
        self._config = config
        self._orders = orders
        self._cur_id = 0
        self._positions = []
        self._buys = []
        self._sells = []
        self._strategy_name = config.strategy()
        #strategy_module = __import__(f'cointrader.strategies.{self._strategy_name}', fromlist=[self._strategy_name])
        #strategy_module = __import__(self._strategy_name, fromlist=[f'cointrader.strategies'])

        strategy_module = importlib.import_module(f'cointrader.strategies.{self._strategy_name}')
        self._strategy = getattr(strategy_module, self._strategy_name)(symbol=symbol)
        self._max_positions = config.max_positions()
        self._net_profit_percent = 0.0
        self._stop_loss_percent = config.stop_loss_percent()

        print(f'{self._symbol} Loading strategy: {self._strategy_name} max_positions={self._max_positions}')

    def symbol(self) -> str:
        return self._symbol
    
    def position_count(self) -> int:
        """
        Get the number of positions open
        """
        return len(self._positions)

    def market_preload(self, klines: list[Kline]):
        """
        Preload klines for the strategy
        """
        for kline in klines:
            self._strategy.update(kline)

    def market_update(self, kline: Kline):
        self._strategy.update(kline)
        # if position has been closed, remove it from the list
        for position in self._positions:
            if position.closed():
                profit_percent = position.profit_percent()
                if profit_percent > 0:
                    print(f"{Fore.GREEN}{self._symbol} Profit: {position.profit_percent()}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}{self._symbol} Profit: {position.profit_percent()}{Style.RESET_ALL}")
                self._net_profit_percent += profit_percent

                if self._config.simulate():
                    self._buys.append(position.buy_info())
                    self._sells.append(position.sell_info())
                self._positions.remove(position)
                continue
            position.market_update(kline)

        # check if we have too many positions
        if len(self._positions) > self._max_positions:
            return

        # Open a position on a buy signal
        if self._strategy.buy() and len(self._positions) < self._max_positions:
            print(f'Buy signal for {self._symbol}')
            size = self._account.round_base(self._symbol, self._config.max_position_quote_size() / kline.close)
            if size < self._account.get_base_min_size(self._symbol):
                print(f"Size too small: {size}")
                return
            position = TraderPosition(symbol=self._symbol, id=self._cur_id, strategy=self._strategy, execute=self._execute, config=self._config, orders=self._orders)
            position.open_position(price=kline.close, stop_loss=0, size=size, timestamp=kline.ts)
            self._positions.append(position)
            self._cur_id += 1

        strategy_sell_signal = self._strategy.sell()

        # Close a position on a sell signal
        if len(self._positions) > 0:
            print(f'Sell signal for {self._symbol}')
            for position in self._positions:
                sell_signal = False
                if strategy_sell_signal:
                    sell_signal = True
                elif position.current_position_percent(kline.close) < -self._stop_loss_percent:
                    sell_signal = True

                if sell_signal and not position.closed_position():
                    position.close_position(price=kline.close, timestamp=kline.ts)

    def net_profit_percent(self) -> float:
        return self._net_profit_percent

    def buys(self) -> list:
        return self._buys
    
    def sells(self) -> list:
        return self._sells