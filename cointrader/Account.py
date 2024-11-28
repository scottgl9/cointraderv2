from cointrader.base.AccountBase import AccountBase
from cointrader.client.TraderClientBase import TraderClientBase
from cointrader.common.AssetInfo import AssetInfo
from cointrader.common.AssetInfoConfig import AssetInfoConfig

class Account(AccountBase):
    _asset_info = None
    def __init__(self, client: TraderClientBase, asset_info=None, logger=None):
        super().__init__(logger)
        if not asset_info:
            name = client.name()
            asset_info = AssetInfoConfig(f'{name}_asset_info.json')
        self._asset_info = asset_info
        self._balances = {}
        self._tickers_info = {}
        self._client = client

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

    def load_asset_info(self):
        if not self._asset_info.file_exists():
            self._asset_info.fetch()
        else:
            self._asset_info.load()

    def save_asset_info(self):
        self._asset_info.save()

    def get_asset_info(self, symbol) -> AssetInfo:
        return self._asset_info.get_asset_info(symbol)
