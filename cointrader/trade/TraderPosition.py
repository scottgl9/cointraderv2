from cointrader.common.Strategy import Strategy
from cointrader.common.Kline import Kline
from .TraderConfig import TraderConfig

def TraderPosition(object):
    _symbol = None
    _config = None
    def __init__(self, symbol: str, strategies: list[Strategy], config: TraderConfig):
        self._symbol = symbol
        self._config = config
        self._strategies = strategies
        self._close_position = False
        self.position = 0
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        self.current_price = 0
        self.pnl = 0
        self.pnl_percent = 0
        self.timestamp = 0

    def market_update(self, kline: Kline):
        for strategy in self._strategies:
            strategy.update(kline)
    
    def closed(self):
        return self._close_position
