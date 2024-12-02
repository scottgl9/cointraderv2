from cointrader.common.SymbolInfo import SymbolInfo
from cointrader.market.MarketBase import MarketBase
from cointrader.client.TraderClientBase import TraderClientBase

class AccountBase(object):
    _logger = None
    _name = None
    _client = None
    _market = None
    def __init__(self, client: TraderClientBase, market: MarketBase, logger=None):
        self._cxlent = client
        self._market = market
        self._logger = logger

    def name(self):
        return self._name

    def client(self):
        raise NotImplementedError

    def get_account_balances(self) -> dict:
        raise NotImplementedError

    def get_total_balance(self, currency : str) -> float:
        raise NotImplementedError

    def get_asset_balance(self, asset : str) -> tuple[float, float]:
        raise NotImplementedError

    def update_asset_balance(self, asset: str, available: float, hold: float):
        raise NotImplementedError
    
    def load_symbol_info(self) -> bool:
        raise NotImplementedError
    
    def save_symbol_info(self) -> bool:
        raise NotImplementedError
    
    def get_symbol_info(self, symbol) -> SymbolInfo:
        raise NotImplementedError
