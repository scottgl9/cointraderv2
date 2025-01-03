from .Trader import Trader
from .TraderConfig import TraderConfig
from cointrader.order.Orders import Orders
from cointrader.execute.ExecuteBase import ExecuteBase
from cointrader.execute.pipeline.ExecutePipeline import ExecutePipeline
from cointrader.account.AccountBase import AccountBase
from cointrader.common.Kline import Kline
from cointrader.common.LogLevel import LogLevel

class MultiTrader(object):
    def __init__(self, account: AccountBase, exec_pipe: ExecutePipeline, config: TraderConfig, orders: Orders = None, restore_positions = False, granularity: int = 0, strategy_weights: dict[str, float] = None):
        self._traders: dict[str, Trader] = {}
        self._account = account
        self._config = config
        self._exec_pipe = exec_pipe
        self._granularity = granularity
        self._max_positions = self._config.max_positions()
        self._position_count_per_symbol = {}

        # set default temporary global config
        self._config.set_global_disable_new_positions(False)
        self._config.set_global_current_balance_quote(0.0)
        self._config.set_global_last_closed_position_profit(0.0)

        if not orders:
            self._orders = Orders(config=self._config)
        else:
            self._orders = orders
        self._symbols = self._config.trade_symbols()

        if self._config.log_level() >= LogLevel.INFO.value:
            print(f"MultiTrader: strategy: {self._config.strategy()} trade_quote_size: {self._config.max_position_quote_size()} max_positions: {self._config.max_positions()} symbols: {self._symbols} ")

        for symbol in self._symbols:
            if symbol not in self._traders.keys():
                self._traders[symbol] = Trader(account=account, symbol=symbol, exec_pipe=self._exec_pipe, config=self._config, orders=self._orders, granularity=self._granularity, strategy_weights=strategy_weights)
                # restore previously open positions if needed
                if restore_positions:
                    self._traders[symbol].restore_positions(current_price=0.0, current_ts=0)

    def market_update_quote_balance(self, quote_name: str):
        """
        Update the current unrounded quote balance before running market_update_price()
        The purpose is to prevent checking quote balance too many times during live trading (so we don't get blocked by the API)
        """
        balance, _ = self._account.get_asset_balance(quote_name, round=False)
        self._config.set_global_current_balance_quote(balance)
        global_balance = self._config.global_current_balance_quote()
        if global_balance != balance:
            print(f"{balance} != {global_balance}")


    def market_preload(self, symbol: str, klines: list[Kline]):
        """
        Preload klines for the strategy of the trader
        """
        if symbol not in self._traders.keys():
            print(f"Symbol {symbol} not found in traders")
            return

        trader = self._traders[symbol]
        trader.market_preload(klines)

    def market_update_kline_other_timeframe(self, symbol: str, kline: Kline, granularity: int, preload: bool = False):
        """
        Update the trader with a kline from another timeframe
        """
        if symbol not in self._traders.keys():
            print(f"Symbol {symbol} not found in traders: {self._traders.keys()}")
            return
        
        trader = self._traders[symbol]
        trader.market_update_kline_other_timeframe(kline=kline, granularity=granularity, preload=preload)

    def market_update_price(self, symbol: str, current_price: float, current_ts: int, granularity: int):
        """
        Update the trader with the current price
        """
        if symbol not in self._traders.keys():
            print(f"Symbol {symbol} not found in traders: {self._traders.keys()}")
            return

        trader = self._traders[symbol]

        self._position_count_per_symbol[symbol] = trader.position_count()

        total_position_count = 0
        for count in self._position_count_per_symbol.values():
            total_position_count += count

        # enforce max position count
        if total_position_count >= self._max_positions:
            #print(f"Max positions reached: {total_position_count} >= {self._max_positions}")
            self._config.set_global_disable_new_positions(True)
            #trader.disable_new_positions(True)
        else:
            self._config.set_global_disable_new_positions(False)
            #trader.disable_new_positions(False)

        trader.market_update_price(current_price=current_price, current_ts=current_ts, granularity=granularity)
        self._position_count_per_symbol[symbol] = trader.position_count()

        last_closed_profit = self._config.global_last_closed_position_profit()
        # for the last profit on close, check if we exceeded the maximum loss
        if last_closed_profit <= self._config.global_disable_after_loss_percent():
            if self._config.log_level() >= LogLevel.INFO.value:
                print(f"Disable after loss of {last_closed_profit}")
            pass

    def market_update_kline(self, symbol: str, kline: Kline, granularity: int):
        """
        Update the trader strategy with the current kline
        """
        if symbol not in self._traders.keys():
            print(f"Symbol {symbol} not found in traders: {self._traders.keys()}")
            return

        trader = self._traders[symbol]
        trader.market_update_kline(kline=kline, granularity=granularity)

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
