# This file is used to define a static stop loss strategy. This strategy is used to set a stop loss price a fixed percent below current or buy price
from cointrader.common.TradeLossBase import TradeLossBase
from cointrader.account.AccountBase import AccountBase
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.common.Kline import Kline

class Static(TradeLossBase):
    def __init__(self, name='trade_loss_static', symbol=None, account=None, config=None):
        super().__init__(name=name, symbol=symbol, account=account, config=config)
        self._stop_loss_percent = self._config.stop_loss_percent()
        self._stop_loss_limit_percent = self._config.stop_loss_limit_order_percent()

    def reset(self):
        pass

    def ready():
        return True

    def get_stop_loss_price(self, price: float, current_ts: int) -> float:
        # set the stop loss price slightly above the limit price (determined by stop_loss_limit_percent)
        stop_price = self._account.round_quote(self._symbol, (1 - ((self._stop_loss_percent - self._stop_loss_limit_percent) / 100.0)) * price)
        return stop_price

    def get_stop_limit_price(self, price: float, current_ts: int) -> float:
        # for the 'stop' price, we use this as the limit price
        limit_price = self._account.round_quote(self._symbol, (1 - (self._stop_loss_percent / 100.0)) * price)
        return limit_price

    def update(self, kline: Kline):
        pass
