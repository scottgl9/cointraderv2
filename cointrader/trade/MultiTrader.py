from .Trader import Trader
from .TraderConfig import TraderConfig
from cointrader.order.Orders import Orders
from cointrader.execute.ExecuteBase import ExecuteBase
from cointrader.account.AccountBase import AccountBase
from cointrader.common.Kline import Kline

class MultiTrader(object):
    def __init__(self, account: AccountBase, execute: ExecuteBase, config: TraderConfig, orders: Orders = None, granularity: int = 0):
        self._traders: dict[str, Trader] = {}
        self._account = account
        self._config = config
        self._execute = execute
        self._granularity = granularity
        self._positions_restored = False

        if not orders:
            self._orders = Orders(config=self._config)
        else:
            self._orders = orders
        self._symbols = self._config.trade_symbols()
        print(f"MultiTrader: {self._symbols}")
        for symbol in self._symbols:
            if symbol not in self._traders.keys():
                self._traders[symbol] = Trader(account=account, symbol=symbol, execute=self._execute, config=self._config, orders=self._orders, granularity=self._granularity)


    def market_preload(self, symbol: str, klines: list[Kline]):
        """
        Preload klines for the strategy of the trader
        """
        if symbol not in self._traders.keys():
            print(f"Symbol {symbol} not found in traders")
            return

        trader = self._traders[symbol]
        trader.market_preload(klines)

    def market_update(self, kline: Kline, current_price: float, current_ts: int, granularity: int):
        if kline.symbol not in self._traders.keys():
            print(f"Symbol {kline.symbol} not found in traders")
            return

        # restore positions for living trading
        if not self._config.simulate() and not self._positions_restored:
            for symbol in self._symbols:
                self._traders[symbol].restore_positions()
            self._positions_restored = True

        trader = self._traders[kline.symbol]
        trader.market_update(kline, current_price=current_price, current_ts=current_ts, granularity=granularity)

    def net_profit_percent(self, symbol: str):
        if symbol not in self._traders.keys():
            return 0.0
        return self._traders[symbol].net_profit_percent()

    def positive_profit_percent(self, symbol: str):
        if symbol not in self._traders.keys():
            return 0.0
        return self._traders[symbol].positive_profit_percent()
    
    def negative_profit_percent(self, symbol: str):
        if symbol not in self._traders.keys():
            return 0.0
        return self._traders[symbol].negative_profit_percent()

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
