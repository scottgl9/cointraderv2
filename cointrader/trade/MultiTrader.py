from .Trader import Trader
from .TraderConfig import TraderConfig
from cointrader.Account import Account

class MultiTrader(object):
    def __init__(self, account: Account, config: TraderConfig):
        self._traders = {}
        self._account = account
        self._config = config
        self._symbols = self._config.trade_symbols()
        print(f"MultiTrader: {self._symbols}")
        for symbol in self._symbols:
            if symbol not in self._traders.keys():
                self._traders[symbol] = Trader(account=account, symbol=symbol, config=self._config)

    def market_update(self, kline):
        if not kline.symbol in self._traders.keys():
            return

        trader = self._traders[kline.symbol]
        trader.market_update(kline)
