from cointrader.common.SymbolInfo import SymbolInfo
from cointrader.market.MarketBase import MarketBase
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from decimal import Decimal

class AccountBase(object):
    _logger = None
    _name = None
    _exchange = None
    _market = None
    def __init__(self, exchange: TraderExchangeBase, market: MarketBase, logger=None):
        self._cxlent = exchange
        self._market = market
        self._logger = logger

    def name(self):
        return self._name

    def exchange(self):
        raise NotImplementedError

    def round_base(self, symbol: str, amount: Decimal) -> Decimal:
        """
        Round the amount to the base precision
        """
        raise NotImplementedError

    def round_quote(self, symbol: str, amount: Decimal) -> Decimal:
        """
        Round the amount to the quote precision
        """
        raise NotImplementedError

    def get_account_balances(self) -> dict:
        raise NotImplementedError

    def get_total_balance(self, currency : str) -> Decimal:
        raise NotImplementedError

    def get_asset_balance(self, asset : str) -> tuple[Decimal, Decimal]:
        raise NotImplementedError

    def update_asset_balance(self, asset: str, available: Decimal, hold: Decimal):
        raise NotImplementedError
    
    def load_symbol_info(self) -> bool:
        raise NotImplementedError
    
    def save_symbol_info(self) -> bool:
        raise NotImplementedError
    
    def get_symbol_info(self, symbol) -> SymbolInfo:
        raise NotImplementedError
