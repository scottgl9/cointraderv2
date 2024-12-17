# This file is used to define a Chandelier Exit for trailing stop loss strategy. This strategy is used to set a stop loss price based on the highest high price over a period of time.
from collections import deque
from cointrader.common.TradeLossBase import TradeLossBase
from cointrader.account.AccountBase import AccountBase
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.common.Kline import Kline
from cointrader.indicators.ATR import ATR

class ChandelierExit(TradeLossBase):
    def __init__(self, name='trade_loss_chandelier_exit', symbol=None, account=None, config=None):
        super().__init__(name=name, symbol=symbol, account=account, config=config)
        self._period = 22
        self._stop_loss_limit_percent = self._config.stop_loss_limit_order_percent()
        self._atr = ATR(period=self._period)
        self._multiplier = 3.0
        self._highs = deque(maxlen=self._period)
        self._lows = deque(maxlen=self._period)

    def reset(self):
        self._atr.reset()
        self._highs.clear()
        self._lows.clear()

    def ready(self) -> bool:
        return len(self._highs) == self._period

    def get_stop_loss_price(self, price: float, current_ts: int) -> float:
        highest_high = max(self._highs)
        stop_limit_price = highest_high - self._multiplier * self._atr.get_last_value()
        # Stop price is set slightly above the stop limit price
        stop_price = self._account.round_quote(self._symbol, stop_limit_price * (1.0 + self._stop_loss_limit_percent / 100.0))
        return stop_price

    def get_stop_limit_price(self, price: float, current_ts: int) -> float:
        highest_high = max(self._highs)
        stop_limit_price = self._account.round_quote(self._symbol, highest_high - self._multiplier * self._atr.get_last_value())
        return stop_limit_price

    def update(self, kline: Kline, current_price: float, current_ts: int):
        self._atr.update(kline)
        self._highs.append(kline.high)
        self._lows.append(kline.low)
