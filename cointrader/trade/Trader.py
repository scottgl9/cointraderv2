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
        print(f'Loading strategy: {self._strategy_name}')
        strategy_module = importlib.import_module(f'cointrader.strategies.{self._strategy_name}')
        self._strategy = getattr(strategy_module, self._strategy_name)(symbol=symbol)
        self._max_positions = config.max_positions()

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
                self._positions.remove(position)
                continue
            position.market_update(kline)
        
        if len(self._positions) > self._max_positions:
            return

        # Open a position on a buy signal
        if self._strategy.buy():
            position = TraderPosition(symbol=self._symbol, strategy=self._strategy, config=self._config)

        # Close a position on a sell signal
        if self._strategy.sell():
            for position in self._positions:
                position.close_position(price=kline.close, timestamp=kline.timestamp)

    def get_total_profit(self, currency: str) -> float:
        pass
