# Thik file is used to define a static trade size strategy. This strategy is used to set a trade size based on a fixed amount of the quote currency
from cointrader.common.TradeSizeBase import TradeSizeBase
from cointrader.account.AccountBase import AccountBase
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.common.Kline import Kline

class Fixed(TradeSizeBase):
    def __init__(self, name='trade_size_fixed', symbol=None, account=None, config=None):
        super().__init__(name=name, symbol=symbol, account=account, config=config)
        self._max_position_quote_size = self._config.max_position_quote_size

    def get_base_trade_size(self, current_price: float, current_ts: int) -> float:
        if current_price > 0:
            size = self._account.round_base(self._symbol, self._config.max_position_quote_size() / current_price)
            if size < self._account.get_base_min_size(self._symbol):
                print(f"{self._symbol} Size too small: {size}")
                return None
            return size
        return None

    def get_quote_trade_size(self, current_price: float, current_ts: int) -> float:
        return self._max_position_quote_size

    def update(self, kline: Kline, current_price: float, current_ts: int):
        pass
