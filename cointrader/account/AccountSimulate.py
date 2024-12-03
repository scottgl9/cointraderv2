# Same as Account class, but simulates account balances

from .AccountBase import AccountBase
from cointrader.client.TraderClientBase import TraderClientBase
from cointrader.common.SymbolInfo import SymbolInfo
from cointrader.common.SymbolInfoConfig import SymbolInfoConfig
from cointrader.market.MarketBase import MarketBase

class AccountSimulate(AccountBase):
    _symbol_info = None
    def __init__(self, client: TraderClientBase, market: MarketBase, symbol_info=None, logger=None):
        super().__init__(client=client, market=market, logger=logger)
        self._name = client.name()
        if not symbol_info:
            symbol_info = SymbolInfoConfig(client=client, path=f'{self._name}_symbol_info.json')
        self._symbol_info = symbol_info
        self._balances = {}
        self._tickers_info = {}
        self._client = client
    
    def client(self) -> TraderClientBase:
        return self._client

    def get_account_balances(self) -> dict:
        """
        Get the account balances
        """
        return self._balances

    def get_total_balance(self, currency : str) -> float:
        """
        Get the total balance of a currency
        """

        # if currency is for example BTC, we need to first convert it to a stable currency
        stable_currencies = self._client.info_get_stable_currencies()
        currency_stable_price = 1.0
        if currency not in stable_currencies:
            currency_stable_price = 0.0
            for stable in stable_currencies:
                symbol = self._client.info_ticker_join(currency, stable)
                try:
                    currency_stable_price = self._market.market_ticker_price_get(ticker=symbol)
                    break
                except NotImplementedError:
                    continue

        if currency_stable_price == 0.0:
            raise ValueError(f'Currency {currency} not found in {stable_currencies}')

        currencies = self._client.info_quote_currencies_list()
        if currency not in currencies:
            raise ValueError(f'Currency {currency} not found in {currencies}')
        try:
            prices = self._market.market_ticker_prices_all_get()
        except NotImplementedError:
            prices = {}
            for c in currencies:
                symbol = self._client.info_ticker_join(c, currency)
                prices[symbol] = self._market.market_ticker_price_get(ticker=symbol)
    
        total_balance = 0.0
        for asset, (balance, available) in self.get_account_balances().items():
            total = balance + available
            if total == 0.0:
                continue

            if asset == currency:
                total_balance += total
                continue

            if currency not in stable_currencies:
                symbol = self._client.info_ticker_join(asset, currency)
                if symbol in prices:
                    total_balance += total * prices[symbol]
                #else:
                #    print(symbol)
            else:
                # if trade pair exists, just add it to the total
                symbol = self._client.info_ticker_join(asset, currency)
                if symbol in prices:
                    total_balance += total * prices[symbol]
                else:
                    # if there is not an existing trade pair, try to convert from an equivalent stable currency
                    for equivalent in self._client.info_equivalent_stable_currencies():
                        symbol = self._client.info_ticker_join(asset, equivalent)
                        if symbol in prices:
                            print(f'Converting {asset} to {currency} using {equivalent}')
                            total_balance += total * prices[symbol]
                            break

        return total_balance

    def get_asset_balance(self, asset : str) -> tuple[float, float]:
        """
        Get the asset balance
        """
        try:
            return self._balances[asset]
        except KeyError:
            return 0.0, 0.0

    def update_asset_balance(self, asset, available: float, hold: float):
        """
        Update the asset balance
        """
        self._balances[asset] = (available, hold)

    def load_symbol_info(self):
        """
        Load the information for all symbols
        """
        print(f'Loading symbol info from {self._name}')
        if not self._symbol_info.file_exists():
            print(f'Loading symbol info from {self._name}')
            if not self._symbol_info.fetch():
                return False
            self.save_symbol_info()
        else:
            self._symbol_info.load()
        return True

    def save_symbol_info(self):
        """
        Save the information for all symbols to a file
        """
        self._symbol_info.save()

    def get_symbol_info(self, symbol) -> SymbolInfo:
        """
        Get the information for a symbol
        """
        return self._symbol_info.get_symbol_info(symbol)
