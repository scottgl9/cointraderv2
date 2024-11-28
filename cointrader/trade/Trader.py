# Using market and account info, creates TraderPosition for a given symbol when entered into a position
# Trader only operates on a designated symbol
from cointrader.common.Kline import Kline
from cointrader.common.Strategy import Strategy
from cointrader.Account import Account
from .TraderConfig import TraderConfig

def Trader(object):
    _symbol = None
    _positions = []
    _strategy_name = None
    _max_positions = 0

    def __init__(self, account: Account, symbol: str, config: TraderConfig):
        self._symbol = symbol
        self._config = config
        self._positions = []
        self._strategy_name = config.strategy()
        self._max_positions = config.max_positions()

    def symbol(self) -> str:
        return self._symbol

    def market_update(self, kline: Kline):
        for position in self._positions:
            if position.closed():
                self._positions.remove(position)
                continue
            position.market_update(kline)

    def get_total_profit(self, currency: str) -> float:
        pass
