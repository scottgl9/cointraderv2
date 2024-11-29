# Using market and account info, creates TraderPosition for a given symbol when entered into a position
# Trader only operates on a designated symbol
from cointrader.common.Kline import Kline
from cointrader.common.Strategy import Strategy
from cointrader.Account import Account
from .TraderConfig import TraderConfig
import importlib

class Trader(object):
    _symbol = None
    _account = None
    _positions = []
    _strategy_name = None
    _strategy = None
    _max_positions = 0

    def __init__(self, account: Account, symbol: str, config: TraderConfig):
        self._symbol = symbol
        self._account = account
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

    def get_total_profit(self, currency: str) -> float:
        pass
