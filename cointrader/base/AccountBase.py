from cointrader.common.SymbolInfo import SymbolInfo

class AccountBase(object):
    _logger = None
    _name = None

    def __init__(self, logger=None):
        self.logger = logger

    def get_account_balances(self) -> dict:
        raise NotImplementedError

    def get_total_balance(self, currency : str) -> float:
        raise NotImplementedError

    def get_asset_balance(self, asset : str) -> tuple[float, float]:
        raise NotImplementedError

    def update_asset_balance(self, asset, available: float, hold: float):
        raise NotImplementedError
    
    def load_symbol_info(self):
        raise NotImplementedError
    
    def save_symbol_info(self):
        raise NotImplementedError
    
    def get_symbol_info(self, symbol) -> SymbolInfo:
        raise NotImplementedError
