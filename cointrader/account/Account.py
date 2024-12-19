from .AccountBase import AccountBase
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from cointrader.market.MarketBase import MarketBase
from cointrader.common.SymbolInfo import SymbolInfo
from cointrader.common.SymbolInfoConfig import SymbolInfoConfig
from cointrader.common.AssetInfo import AssetInfo
from cointrader.common.AssetInfoConfig import AssetInfoConfig

class Account(AccountBase):
    _exchange: TraderExchangeBase = None
    _market: MarketBase = None
    _symbol_info: SymbolInfo = None
    _asset_info: AssetInfo = None

    def __init__(self, exchange: TraderExchangeBase, market: MarketBase, symbol_info: SymbolInfo=None, asset_info: AssetInfo=None, logger=None):
        name = exchange.name()
        if not symbol_info:
            symbol_info = SymbolInfoConfig(exchange=exchange, path=f'config/{name}_symbol_info.json')
        if not asset_info:
            asset_info = AssetInfoConfig(exchange=exchange, path=f'config/{name}_asset_info.json')
        super().__init__(exchange=exchange, market=market, symbol_info=symbol_info, asset_info=asset_info, logger=logger)
        self._balances = {}
        self._tickers_info = {}

    def get_base_precision(self, symbol: str) -> int:
        """
        Get the base precision
        """
        try:
            return self._symbol_info.get_symbol_info(symbol).base_precision
        except KeyError:
            return 8

    def get_quote_precision(self, symbol: str) -> int:
        """
        Get the quote precision
        """
        try:
            return self._symbol_info.get_symbol_info(symbol).quote_precision
        except KeyError:
            return 8

    def get_base_min_size(self, symbol: str) -> float:
        """
        Get the base min size
        """
        try:
            return self._symbol_info.get_symbol_info(symbol).base_min_size
        except KeyError:
            return 0.0

    def get_quote_min_size(self, symbol: str) -> float:
        """
        Get the quote min size
        """
        try:
            return self._symbol_info.get_symbol_info(symbol).quote_min_size
        except KeyError:
            return 0.0

    def round_base(self, symbol: str, amount: float) -> float:
        """
        Round the amount to the base precision
        """
        try:
            base_precision = self._symbol_info.get_symbol_info(symbol).base_precision
        except KeyError:
            base_precision = 8

        amount_str = f"{amount:.{base_precision}f}"
        #print(f'round_base: {symbol} {amount} -> {amount_str}')
        return float(amount_str)

    def round_quote(self, symbol: str, amount: float) -> float:
        """
        Round the amount to the quote precision
        """
        try:
            quote_precision = self._symbol_info.get_symbol_info(symbol).quote_precision
        except KeyError:
            quote_precision = 8

        amount_str = f"{amount:.{quote_precision}f}"
        #print(f'round_quote: {symbol} {amount} -> {amount_str} {quote_precision}')
        return float(amount_str)
    
    def round_asset(self, asset: str, amount: float) -> float:
        """
        Round the amount to the asset precision
        """
        asset_precision = 8
        try:
            asset_info = self._asset_info.get_asset_info(asset)
            if asset_info:
                asset_precision = asset_info.precision
        except KeyError:
            pass

        amount_str = f"{amount:.{asset_precision}f}"
        #print(f'round_asset: {asset} {amount} -> {amount_str} {asset_precision}')
        return float(amount_str)

    def get_all_prices(self) -> dict:
        """
        Get all the current prices
        """
        return self._market.market_ticker_prices_all_get()

    def get_account_balances(self, round=False) -> dict:
        """
        Get the account balances
        """
        result = {}
        balances = self._exchange.balance_all_get()
        for asset, (balance, hold) in balances.items():
            if round and balance != 0:
                balance = self.round_asset(asset, balance)
            if round and hold != 0:
                hold = self.round_asset(asset, hold)
            result[asset] = (balance, hold)
        return result

    def get_total_balance(self, currency : str, prices: dict = None) -> float:
        """
        Get the total balance of a currency
        """

        if not prices:
            prices = self._market.market_ticker_prices_all_get()

        # if currency is for example BTC, we need to first convert it to a stable currency
        stable_currencies = self._exchange.info_get_stable_currencies()
        currency_stable_price = 1.0
        if currency not in stable_currencies:
            currency_stable_price = 0.0
            for stable in stable_currencies:
                symbol = self._exchange.info_ticker_join(currency, stable)
                try:
                    currency_stable_price = prices[symbol] #self._market.market_ticker_price_get(ticker=symbol)
                    break
                except NotImplementedError:
                    continue

        if currency_stable_price == 0.0:
            raise ValueError(f'Currency {currency} not found in {stable_currencies}')

        currencies = self._exchange.info_quote_currencies_list()
        if currency not in currencies:
            raise ValueError(f'Currency {currency} not found in {currencies}')
        try:
            prices = self._market.market_ticker_prices_all_get()
        except NotImplementedError:
            prices = {}
            for c in currencies:
                symbol = self._exchange.info_ticker_join(c, currency)
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
                symbol = self._exchange.info_ticker_join(asset, currency)
                if symbol in prices:
                    total_balance += total * prices[symbol]
                #else:
                #    print(symbol)
            else:
                # if trade pair exists, just add it to the total
                symbol = self._exchange.info_ticker_join(asset, currency)
                if symbol in prices:
                    total_balance += total * prices[symbol]
                else:
                    # if there is not an existing trade pair, try to convert from an equivalent stable currency
                    for equivalent in self._exchange.info_equivalent_stable_currencies():
                        symbol = self._exchange.info_ticker_join(asset, equivalent)
                        if symbol in prices:
                            print(f'Converting {asset} to {currency} using {equivalent}')
                            total_balance += total * prices[symbol]
                            break

        return self.round_asset(currency, total_balance)

    def get_asset_balance(self, asset : str, round=False) -> tuple[float, float]:
        """
        Get the asset balance
        """
        balance, hold = self._exchange.balance_get(asset)
        if round and balance != 0:
            balance = self.round_asset(asset, balance)
        if round and hold != 0:
            hold = self.round_asset(asset, hold)
        return tuple([balance, hold])

    def update_asset_balance(self, asset: str, available: float, hold: float):
        """
        Update the asset balance
        """
        self._balances[asset] = {'available': available, 'hold': hold}
        return self._exchange.balance_set(asset, available, hold)

    def get_symbol_list(self):
        return self._symbol_info.get_symbol_list()

    def load_symbol_info(self) -> bool:
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

    def save_symbol_info(self) -> bool:
        """
        Save the information for all symbols to a file
        """
        self._symbol_info.save()

    def get_symbol_info(self, symbol) -> SymbolInfo:
        """
        Get the information for a symbol
        """
        return self._symbol_info.get_symbol_info(symbol)

    def load_asset_info(self) -> bool:
        """
        Load the information for all assets
        """
        print(f'Loading asset info from {self._name}')
        if not self._asset_info.file_exists():
            print(f'Loading asset info from {self._name}')
            if not self._asset_info.fetch():
                print(f'Error fetching asset info')
                return False
            self.save_asset_info()
        else:
            self._asset_info.load()
        return True

    def save_asset_info(self) -> bool:
        """
        Save the information for all assets to a file
        """
        self._asset_info.save()

    def get_asset_info(self, asset) -> AssetInfo:
        """
        Get the information for an asset
        """
        return self._asset_info.get_asset_info(asset)
