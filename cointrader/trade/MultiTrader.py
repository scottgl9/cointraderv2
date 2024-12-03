from .Trader import Trader
from .TraderConfig import TraderConfig
from cointrader.execute.ExecuteBase import ExecuteBase
from cointrader.account.AccountBase import AccountBase

class MultiTrader(object):
    def __init__(self, account: AccountBase, execute: ExecuteBase, config: TraderConfig):
        self._traders = {}
        self._account = account
        self._config = config
        self._execute = execute
        self._symbols = self._config.trade_symbols()
        print(f"MultiTrader: {self._symbols}")
        for symbol in self._symbols:
            if symbol not in self._traders.keys():
                self._traders[symbol] = Trader(account=account, symbol=symbol, execute=self._execute, config=self._config)

    def market_update(self, kline):
        if kline.symbol not in self._traders.keys():
            return
        
        trader = self._traders[kline.symbol]
        trader.market_update(kline)
