# Using market and account info, creates TraderPosition for a given symbol when entered into a position
# Trader only operates on a designated symbol
from cointrader.common.Kline import Kline
from cointrader.common.Strategy import Strategy
from cointrader.account.Account import Account
from .TraderConfig import TraderConfig
from cointrader.execute.ExecuteBase import ExecuteBase
from .TraderPosition import TraderPosition
import importlib

class Trader(object):
    _symbol = None
    _account = None
    _positions = []
    _strategy_name = None
    _strategy = None
    _max_positions = 0

    def __init__(self, account: Account, symbol: str, execute: ExecuteBase, config: TraderConfig):
        self._symbol = symbol
        self._account = account
        self._execute = execute
        self._config = config
        self._positions = []
        self._strategy_name = config.strategy()
        #strategy_module = __import__(f'cointrader.strategies.{self._strategy_name}', fromlist=[self._strategy_name])
        #strategy_module = __import__(self._strategy_name, fromlist=[f'cointrader.strategies'])

        strategy_module = importlib.import_module(f'cointrader.strategies.{self._strategy_name}')
        self._strategy = getattr(strategy_module, self._strategy_name)(symbol=symbol)
        self._max_positions = config.max_positions()

        print(f'{self._symbol} Loading strategy: {self._strategy_name} max_positions={self._max_positions}')

    def symbol(self) -> str:
        return self._symbol
    
    def market_preload(self, klines: list[Kline]):
        """
        Preload klines for the strategy
        """
        for kline in klines:
            self._strategy.update(kline)

    def market_update(self, kline: Kline):
        self._strategy.update(kline)

        for position in self._positions:
            if position.closed():
                print(f"{self._symbol} Profit: {position.profit_percent()}")
                self._positions.remove(position)
                continue
            position.market_update(kline)
        
        if len(self._positions) > self._max_positions:
            return

        # Open a position on a buy signal
        if self._strategy.buy() and len(self._positions) < self._max_positions:
            print(f'Buy signal for {self._symbol}')
            size = self._config.max_position_quote_size() / kline.close
            position = TraderPosition(symbol=self._symbol, strategy=self._strategy, execute=self._execute, config=self._config)
            position.open_position(price=kline.close, stop_loss=0, size=size, timestamp=kline.ts)
            self._positions.append(position)

        # Close a position on a sell signal
        if self._strategy.sell() and len(self._positions) > 0:
            print(f'Sell signal for {self._symbol}')
            for position in self._positions:
                position.close_position(price=kline.close, timestamp=kline.ts)

    def get_total_profit(self, currency: str) -> float:
        pass
