from cointrader.base.AccountBase import AccountBase
from cointrader.client.TraderClientBase import TraderClientBase
from cointrader.common.SymbolInfo import SymbolInfo
from cointrader.common.SymbolInfoConfig import SymbolInfoConfig

class Account(AccountBase):
    _symbol_info = None
    _name = None
    def __init__(self, client: TraderClientBase, symbol_info=None, logger=None):
        super().__init__(logger)
        self._name = client.name()
        if not symbol_info:
            symbol_info = SymbolInfoConfig(f'{self._name}_symbol_info.json')
        self._symbol_info = symbol_info
        self._balances = {}
        self._tickers_info = {}
        self._client = client

    def name(self):
        return self._name

    def get_account_balances(self) -> dict:
        return self._client.balance_all_get()

    def get_total_balance(self, currency : str) -> float:
        currencies = self._client.info_quote_currencies_list()
        if currency not in currencies:
            raise ValueError(f'Currency {currency} not found in {currencies}')

    def get_asset_balance(self, asset : str) -> tuple[float, float]:
        return self._client.balance_get(asset)

    def update_asset_balance(self, asset, available: float, hold: float):
        self._balances[asset] = {'available': available, 'hold': hold}
        return self._client.balance_set(asset, available, hold)

    def load_symbol_info(self):
        if not self._symbol_info.file_exists():
            if not self._symbol_info.fetch():
                return False
        else:
            self._symbol_info.load()
        return True

    def save_symbol_info(self):
        self._symbol_info.save()

    def get_symbol_info(self, symbol) -> SymbolInfo:
        return self._symbol_info.get_symbol_info(symbol)
