from cointrader.common.SymbolInfo import SymbolInfo
from cointrader.common.AssetInfo import AssetInfo
from cointrader.market.MarketBase import MarketBase
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase

class AccountBase(object):
    _logger = None
    _name = None
    _exchange: TraderExchangeBase = None
    _market: MarketBase = None
    _symbol_info: SymbolInfo = None
    _asset_info: AssetInfo = None
    def __init__(self, exchange: TraderExchangeBase, market: MarketBase, symbol_info: SymbolInfo=None, asset_info: AssetInfo=None, logger=None):
        self._name = exchange.name()
        self._exchange = exchange
        self._market = market
        self._symbol_info = symbol_info
        self._asset_info = asset_info
        self._logger = logger

    def name(self) -> str:
        return self._name

    def exchange(self) -> TraderExchangeBase:
        return self._exchange

    def get_base_name(self, symbol: str) -> str:
        """
        Get the base name
        """
        return self._exchange.info_ticker_get_base(symbol)

    def get_quote_name(self, symbol: str) -> str:
        """
        Get the quote name
        """
        return self._exchange.info_ticker_get_quote(symbol)

    def get_base_precision(self, symbol: str) -> int:
        """
        Get the base precision
        """
        raise NotImplementedError

    def get_quote_precision(self, symbol: str) -> int:
        """
        Get the quote precision
        """
        raise NotImplementedError

    def get_base_min_size(self, symbol: str) -> float:
        """
        Get the base min size
        """
        raise NotImplementedError

    def get_quote_min_size(self, symbol: str) -> float:
        """
        Get the quote min size
        """
        raise NotImplementedError

    def round_base(self, symbol: str, amount: float) -> float:
        """
        Round the amount to the base precision
        """
        raise NotImplementedError

    def round_quote(self, symbol: str, amount: float) -> float:
        """
        Round the amount to the quote precision
        """
        raise NotImplementedError

    def round_asset(self, asset: str, amount: float) -> float:
        """
        Round the amount to the asset precision
        """
        raise NotImplementedError

    def get_all_prices(self) -> dict:
        """
        Get all current prices
        """
        raise NotImplementedError

    def get_account_balances(self, round: bool) -> dict:
        raise NotImplementedError

    def get_total_balance(self, currency : str, prices: dict = None) -> float:
        raise NotImplementedError

    def get_asset_balance(self, asset : str, round: bool) -> tuple[float, float]:
        raise NotImplementedError

    def update_asset_balance(self, asset: str, available: float, hold: float):
        raise NotImplementedError
    
    def load_symbol_info(self) -> bool:
        raise NotImplementedError
    
    def save_symbol_info(self) -> bool:
        raise NotImplementedError

    def get_symbol_list(self) -> list[str]:
        """
        Get the list of all tradable symbols
        """
        raise NotImplementedError

    def get_symbol_info(self, symbol) -> SymbolInfo:
        raise NotImplementedError

    def load_asset_info(self) -> bool:
        """
        Load the information for all assets
        """
        raise NotImplementedError

    def save_asset_info(self) -> bool:
        """
        Save the information for all assets to a file
        """
        raise NotImplementedError

    def get_asset_info(self, asset) -> AssetInfo:
        """
        Get the information for an asset
        """
        return NotImplementedError
