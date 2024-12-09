from .Trader import Trader
from .TraderConfig import TraderConfig
from cointrader.order.Orders import Orders
from cointrader.execute.ExecuteBase import ExecuteBase
from cointrader.account.AccountBase import AccountBase

class MultiTrader(object):
    def __init__(self, account: AccountBase, execute: ExecuteBase, config: TraderConfig, orders: Orders = None):
        self._traders = {}
        self._account = account
        self._config = config
        self._execute = execute
        if not self._orders:
            self._orders = Orders()
        else:
            self._orders = orders
        self._symbols = self._config.trade_symbols()
        print(f"MultiTrader: {self._symbols}")
        for symbol in self._symbols:
            if symbol not in self._traders.keys():
                self._traders[symbol] = Trader(account=account, symbol=symbol, execute=self._execute, config=self._config, orders=self._orders)

    def market_update(self, kline):
        if kline.symbol not in self._traders.keys():
            print(f"Symbol {kline.symbol} not found in traders")
            return
        
        trader = self._traders[kline.symbol]
        trader.market_update(kline)

    def net_profit_percent(self, symbol: str):
        if symbol not in self._traders.keys():
            return 0.0
        return self._traders[symbol].net_profit_percent()
    
    def position_count(self, symbol: str):
        if symbol not in self._traders.keys():
            return 0
        return self._traders[symbol].position_count()
    
    def buys(self, symbol: str):
        if symbol not in self._traders.keys():
            return []
        return self._traders[symbol].buys()
    
    def sells(self, symbol: str):
        if symbol not in self._traders.keys():
            return []
        return self._traders[symbol].sells()
