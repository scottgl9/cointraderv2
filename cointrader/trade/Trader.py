# Using market and account info, creates TraderPosition for a given symbol when entered into a position
# Trader only operates on a designated symbol
from cointrader.common.Kline import Kline
from cointrader.common.Strategy import Strategy
from cointrader.account.Account import Account
from .TraderConfig import TraderConfig
from cointrader.execute.ExecuteBase import ExecuteBase
from .TraderPosition import TraderPosition
from cointrader.order.Orders import Orders
from cointrader.order.OrderStatus import OrderStatus
import importlib
from cointrader.signals.EMACross import EMACross
from cointrader.signals.SupertrendSignal import SupertrendSignal
from cointrader.signals.VWAPSignal import VWAPSignal
from colorama import Fore, Back, Style
import time

class Trader(object):
    _symbol = None
    _account = None
    _positions: list[TraderPosition] = []
    _strategy_name = None
    _strategy: Strategy = None
    _max_positions = 0

    def __init__(self, account: Account, symbol: str, execute: ExecuteBase, config: TraderConfig, orders: Orders, granularity: int = 0):
        self._symbol = symbol
        self._account = account
        self._execute = execute
        self._config = config
        self._orders = orders
        self._granularity = granularity
        self._disabled = False
        self._cur_id = 0
        self._positions = []
        self._buys = []
        self._sells = []
        self._strategy_name = config.strategy()
        #strategy_module = __import__(f'cointrader.strategies.{self._strategy_name}', fromlist=[self._strategy_name])
        #strategy_module = __import__(self._strategy_name, fromlist=[f'cointrader.strategies'])

        strategy_module = importlib.import_module(f'cointrader.strategies.{self._strategy_name}')
        self._strategy = getattr(strategy_module, self._strategy_name)(symbol=symbol)
        self._max_positions = config.max_positions()
        self._net_profit_percent = 0.0
        self._positive_profit_percent = 0.0
        self._negative_profit_percent = 0.0
        self._stop_loss_percent = config.stop_loss_percent()
        self._cooldown_period_seconds = config.cooldown_period_seconds()
        self._disable_after_loss_seconds = config.disable_after_loss_seconds()
        self._disable_until_ts = 0
        self._ema_cross = EMACross(name='ema_cross', symbol=symbol, short_period=12, long_period=26)
        self._supertrend = SupertrendSignal(name='supertrend', symbol=symbol, period=20, multiplier=3)
        self._vwap = VWAPSignal(name='vwap', symbol=symbol, period=14)

        print(f'{self._symbol} Loading strategy: {self._strategy_name} max_positions={self._max_positions}')

    def symbol(self) -> str:
        return self._symbol
    
    def position_count(self) -> int:
        """
        Get the number of positions open
        """
        return len(self._positions)

    def market_preload(self, klines: list[Kline]):
        """
        Preload klines for the strategy
        """
        for kline in klines:
            self._strategy.update(kline)

    def market_update(self, kline: Kline, current_price: float):
        # if position has been closed, remove it from the list
        for position in self._positions:
            if kline.granularity == self._granularity:
                position.market_update(current_price)

            if position.opened() and self._config.trailing_stop_loss():
                percent = self._config.stop_loss_percent()
                # set the stop 0.1% above the limit price
                stop_price = self._account.round_quote(self._symbol, (1 - ((percent - 0.1) / 100.0)) * position.buy_price())
                limit_price = self._account.round_quote(self._symbol, (1 - (percent / 100.0)) * position.buy_price())
                # handle setting and updating stop loss orders if enabled
                if not position.stop_loss_is_set():
                    #print(f"buy price: {position.buy_price()} Stop price: {stop_price}")
                    position.create_stop_loss_position(stop_price=stop_price, limit_price=limit_price, timestamp=kline.ts)
                else:
                    # update the stop loss order so it trails the position, if the price has moved up 1%
                    stop_loss_limit_price = position.stop_loss_limit_price()
                    if (current_price - stop_loss_limit_price) / stop_loss_limit_price > 0.01:
                        position.cancel_stop_loss_position()
                        if not self._config.simulate():
                            # wait for the order to be cancelled
                            time.sleep(1)
                        new_stop_price = self._account.round_quote(self._symbol, (1 - ((percent - 0.1) / 100.0)) * current_price)
                        new_stop_limit_price = self._account.round_quote(self._symbol, (1 - (percent / 100.0)) * current_price)
                        #print(f"{self._symbol} Updating stop loss: {stop_loss_limit_price} -> {new_stop_limit_price}")
                        position.create_stop_loss_position(stop_price=new_stop_price, limit_price=new_stop_limit_price, timestamp=kline.ts)

            # handle closed position when sell order or stop loss has been filled
            if position.closed():
                profit_percent = position.profit_percent()
                if profit_percent >= 0:
                    self._positive_profit_percent += profit_percent
                    print(f"{Fore.GREEN}{self._symbol} Profit: {position.profit_percent()}{Style.RESET_ALL}")
                else:
                    self._negative_profit_percent += profit_percent
                    print(f"{Fore.RED}{self._symbol} Profit: {position.profit_percent()}{Style.RESET_ALL}")
                    # Disable opening new positions for a period of time after a loss
                    if self._disable_after_loss_seconds > 0:
                        self._disable_until_ts = kline.ts + self._disable_after_loss_seconds
                        self._disabled = True

                self._net_profit_percent += profit_percent

                if self._config.simulate():
                    self._buys.append(position.buy_info())
                    self._sells.append(position.sell_info())
                self._positions.remove(position)
                continue

        # if kline.granularity != self._granularity:
        #    # handle daily klines
        #    self._supertrend.update(kline)
        #    self._vwap.update(kline)
        #    if self._supertrend.decreasing() and self._vwap.below():
        #        self._disabled = True
        #        self._disable_until_ts = 0
        #    elif self._supertrend.increasing() and self._vwap.above():
        #        self._disabled = False
        #        self._disable_until_ts = 0
        #        #print(f'{Fore.RED}{self._symbol} Supertrend cross down{Style.RESET_ALL}')
        #    return

        self._strategy.update(kline)

        # Disable opening new positions for a period of time after a loss
        if self._disable_until_ts != 0 and kline.ts >= self._disable_until_ts:
            self._disable_until_ts = 0
            self._disabled = False

        # Open a position on a buy signal
        if not self._disabled and self._strategy.buy_signal() and len(self._positions) < self._max_positions:
            size = self._account.round_base(self._symbol, self._config.max_position_quote_size() / kline.close)
            if size < self._account.get_base_min_size(self._symbol):
                print(f"Size too small: {size}")
                return
            #print(f'Buy signal {self._strategy.buy_signal_name()} for {self._symbol}')
            position = TraderPosition(symbol=self._symbol, id=self._cur_id, strategy=self._strategy, execute=self._execute, config=self._config, orders=self._orders)
            position.open_position(price=kline.close, stop_loss=0, size=size, timestamp=kline.ts, current_price=current_price)
            self._positions.append(position)
            self._cur_id += 1
            if self._cooldown_period_seconds > 0:
                self._disabled = True
                self._disable_until_ts = kline.ts + self._cooldown_period_seconds

            # if we have a market order filled immediately, then set the stop loss
            if position.opened() and self._config.trailing_stop_loss():
                percent = self._config.stop_loss_percent()
                stop_price = self._account.round_quote(self._symbol, (1 - (percent / 100.0)) * position.buy_price())
                # handle setting and updating stop loss orders if enabled
                if not position.stop_loss_is_set():
                    #print(f"buy price: {position.buy_price()} Stop price: {stop_price}")
                    position.create_stop_loss_position(stop_price=stop_price, limit_price=stop_price, timestamp=kline.ts)

        strategy_sell_signal = self._strategy.sell_signal()

        # Close a position on a sell signal
        if len(self._positions) > 0:
            for position in self._positions:
                sell_signal = False
                sell_signal_name = None
                if strategy_sell_signal:
                    sell_signal = True
                    sell_signal_name = self._strategy.sell_signal_name()
                #elif position.current_position_percent(kline.close) < -self._stop_loss_percent:
                #    sell_signal = True
                #    sell_signal_name = 'stop_loss'

                if sell_signal and not position.closed_position():
                    #if position.stop_loss_is_set():
                    #    position.cancel_stop_loss_position()
                    #print(f'Sell signal {sell_signal_name} for {self._symbol}')
                    position.close_position(price=kline.close, timestamp=kline.ts)

    def net_profit_percent(self) -> float:
        """
        Get the net profit percent for the symbol
        """
        return self._net_profit_percent

    def positive_profit_percent(self) -> float:
        """
        Get the positive profit percent for the symbol
        """
        return self._positive_profit_percent
    
    def negative_profit_percent(self) -> float:
        """
        Get the negative profit percent for the symbol
        """
        return self._negative_profit_percent

    def buys(self) -> list:
        return self._buys
    
    def sells(self) -> list:
        return self._sells