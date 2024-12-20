# this class implement the base class for trailing trade loss price calculation
from cointrader.account.AccountBase import AccountBase
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.common.Kline import Kline

class TradeLossBase(object):
    _name: str = None
    _account: AccountBase = None
    _config: TraderConfig = None
    _symbol: str = None

    def __init__(self, name: str, symbol: str, account: AccountBase, config: TraderConfig):
        self._name = name
        self._account = account
        self._config = config
        self._symbol = symbol

    def reset(self):
        raise NotImplementedError

    def ready(self) -> bool:
        raise NotImplementedError

    def name(self) -> str:
        return self._name

    def get_stop_loss_price(self, price: float, current_ts: int) -> float:
        raise NotImplementedError

    def get_stop_limit_price(self, price: float, current_ts: int) -> float:
        raise NotImplementedError

    def update(self, kline: Kline):
        raise NotImplementedError
