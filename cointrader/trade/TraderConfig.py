import os
import json
from cointrader.common.LogLevel import LogLevel

# Example of a trade config
DEFAULT_TRADE_CONFIG = {
    # Configuration options set on start
    'simulate': True,                         # Simulate trading without making real trades
    'log_level': LogLevel.INFO.value,         # Log level (4=DEBUG, 3=INFO, 2=WARNING, 1=ERROR, 0=NONE)
    'orders_db_path': 'orders.db',            # Path to the order database
    'market_db_path': 'market_data.db',       # Path to the market database
    'max_position_per_symbol': 1,             # Maximum number of positions to hold per symbol
    'max_positions': 5,                       # Maximum number of positions to hold
    'quote_currency': 'USD',                  # Currency to use for trading
    'max_position_quote_size': 100.0,         # Maximum size of a position in quote currency
    'strategies_other_timeframes': [          # Strategies to use for trading on other timeframes (ex. 1 day)
        'SignalStrength:86400'
    ],
    'strategy': 'SignalStrength',             # Strategy to use for trading with the main timeframe (ex. 1 hour)
    'granularity': 3600,                      # Granularity of the klines to use
    'loss_strategy': 'ChandelierExit',        # Strategy to use for setting stop loss
    'size_strategy': 'Fixed',                 # Strategy to use for setting trade size
    'trade_symbols': ['BTC-USD', 'ETH-USD', 'SOL-USD'],
    'stop_loss_percent': 5.0,                 # percent stop loss to set under the buy price (for fixed stop loss strategy)
    'min_stop_loss_percent': 1.0,             # minimum percent stop loss to set under the buy price (for dynamic stop loss strategy)
    'stop_loss_limit_order_percent': 0.1,     # percent to set the stop loss above or below the limit price
    'limit_order_percent': 0.2,               # percent to set the limit price above or below the current price
    'replace_buy_order_percent': 1.0,         # percent of price movement away from order before buy order gets replaced (limit and stop loss limit orders)
    'replace_sell_order_percent': 1.0,        # percent of price movement away from order before sell order gets replaced (limit and stop loss limit orders)
    'trailing_stop_loss': True,               # stop loss follows the price up
    'min_take_profit_percent': 0.5,           # minimum percent profit to take
    'stop_on_loss': True,                     # Stop trading bot after a loss
    'max_total_loss_percent': 10.0,           # Maximum total loss percent before stopping the bot
    'global_cooldown_period_seconds': 3600,   # Global configuration across all traders, which sets a specific time in seconds between opening new positions
    'cooldown_period_seconds': 3600,          # Local cooldown period after entering a position before opening another (local to each trader)
    'global_disable_after_loss_percent': -3.0,# Percent loss where we disable trading globally with global_disable_after_loss_seconds
    'global_disable_after_loss_seconds': 86400,      # Global config to disable trading after a certain loss percent for this many seconds
    'diable_after_loss_seconds': 3600,        # local config per trader to disable trading after a loss for this many seconds
    'start_position_type': 'STOP_LOSS_LIMIT', # Type of order to open a position (MARKET, LIMIT, STOP_LOSS_LIMIT)
    'end_position_type': 'STOP_LOSS_LIMIT',   # Type of order to open a position (MARKET, LIMIT, STOP_LOSS_LIMIT)
    'sell_all_on_stop': False,                # sell all open positions when the bot stops
    'position_open_buy_complete': True,       # Only allow opening a new position when all existing buy orders (limit) are complete for open positions

    # temporary global configuration options used across all traders
    'tmp_global_disable_new_positions': False,      # global flag to enable/disable opening new positions
    'tmp_global_disable_new_positions_until_ts': 0, # wait until timestamp to globally re-enable opening new positions. Value of zero means it needs to be manually re-enabled
    'tmp_global_current_balance_quote': 0.0,        # global variable to store the current quote balance
    'tmp_global_last_closed_position_profit': 0.0,  # global variable to track the last profit percent of the last position closed
}

class TraderConfig(object):
    def __init__(self, path : str):
        self._path = path
        self._config = DEFAULT_TRADE_CONFIG

    def path(self) -> str:
        return self._path

    def get_config_path(self) -> str:
        return self._path

    def get_config(self):
        return self._config

    def config_file_exists(self) -> bool:
        if os.path.exists(self._path):
            return True
        return False

    def load_config(self) -> bool:
        if not self.config_file_exists():
            return False
        try:
            with open(self._path, 'r') as f:
                self._config = json.load(f)
        except Exception as e:
            print(f"Error loading config from {self.path} {e}: using defaults")
            return False
        return True

    def save_config(self) -> bool:
        try:
            with open(self._path, 'w') as f:
                config = {}
                # do not save temporary keys to the config file
                for name in self._config.keys():
                    if name.startswith('tmp_'):
                        continue
                    config[name] = self._config[name]
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config to {self.path}: {e}")
            return False
        return True

    def get(self, key):
        try: 
            result = self._config.get(key)
        except:
            result = DEFAULT_TRADE_CONFIG[key]
            self.set(key, result)
        return result

    def set(self, key, value):
        self._config[key] = value

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __dict__(self):
        return self._config
    
    def __repr__(self):
        return self.__dict__()

    def simulate(self):
        return self.get('simulate')
    
    def log_level(self) -> int:
        return self.get('log_level')
    
    def set_log_level(self, log_level: int):
        self.set('log_level', log_level)

    def orders_db_path(self):
        return self.get('orders_db_path')

    def market_db_path(self):
        return self.get('market_db_path')

    def max_positions_per_symbol(self):
        return self.get('max_positions_per_symbol')
    
    def set_max_positions_per_symbol(self, max_positions_per_symbol):
        self.set('max_positions_per_symbol', max_positions_per_symbol)

    def max_positions(self):
        return self.get('max_positions')

    def set_max_positions(self, max_positions):
        self.set('max_positions', max_positions)

    def quote_currency(self):
        return self.get('quote_currency')

    def set_quote_currency(self, quote_currency):
        self.set('quote_currency', quote_currency)

    def max_position_quote_size(self):
        return self.get('max_position_quote_size')
    
    def set_max_position_quote_size(self, max_position_quote_size):
        self.set('max_position_quote_size', max_position_quote_size)

    def strategy(self) -> str:
        return self.get('strategy')
    
    def set_strategy(self, strategy: str):
        self.set('strategy', strategy)

    def strategies_other_timeframes(self) -> list[str]:
        """
        Strategies to use for other timeframes, which consist of a time frame/granularity (in seconds) and a strategy
        """
        return self.get('strategies_other_timeframes')

    def set_strategies_other_timeframes(self, strategies: list[str]):
        self.set('strategies_other_timeframes', strategies)

    def granularity(self) -> int:
        return self.get('granularity')

    def loss_strategy(self) -> str:
        return self.get('loss_strategy')
    
    def set_loss_strategy(self, loss_strategy: str):
        self.set('loss_strategy', loss_strategy)

    def size_strategy(self) -> str:
        return self.get('size_strategy')
    
    def set_size_strategy(self, size_strategy: str):
        self.set('size_strategy', size_strategy)

    def trade_symbols(self) -> dict:
        return self.get('trade_symbols')
    
    def set_trade_symbols(self, trade_symbols: dict):
        self.set('trade_symbols', trade_symbols)

    def stop_loss_percent(self) -> float:
        return self.get('stop_loss_percent')
    
    def set_stop_loss_percent(self, stop_loss_percent: float):
        self.set('stop_loss_percent', stop_loss_percent)

    def min_stop_loss_percent(self) -> float:
        return self.get('min_stop_loss_percent')
    
    def set_min_stop_loss_percent(self, min_stop_loss_percent: float):
        self.set('min_stop_loss_percent', min_stop_loss_percent)

    def stop_loss_limit_order_percent(self) -> float:
        return self.get('stop_loss_limit_order_percent')
    
    def set_stop_loss_limit_order_percent(self, stop_loss_limit_order_percent: float):
        self.set('stop_loss_limit_order_percent', stop_loss_limit_order_percent)

    def limit_order_percent(self) -> float:
        return self.get('limit_order_percent')
    
    def set_limit_order_percent(self, limit_order_percent: float):
        self.set('limit_order_percent', limit_order_percent)

    def replace_buy_order_percent(self) -> float:
        return self.get('replace_buy_order_percent')
    
    def set_replace_buy_order_percent(self, replace_buy_order_percent: float):
        self.set('replace_buy_order_percent', replace_buy_order_percent)

    def replace_sell_order_percent(self) -> float:
        return self.get('replace_sell_order_percent')
    
    def set_replace_sell_order_percent(self, replace_sell_order_percent: float):
        self.set('replace_sell_order_percent', replace_sell_order_percent)

    def trailing_stop_loss(self) -> bool:
        return self.get('trailing_stop_loss')
    
    def set_trailing_stop_loss(self, trailing_stop_loss: bool):
        self.set('trailing_stop_loss', trailing_stop_loss)

    def min_take_profit_percent(self) -> float:
        return self.get('min_take_profit_percent')
    
    def set_min_take_profit_percent(self, min_take_profit_percent: float):
        self.set('take_profit_percent', min_take_profit_percent)

    def stop_on_loss(self) -> bool:
        return self.get('stop_on_loss')
    
    def set_stop_on_loss(self, stop_on_loss: bool):
        self.set('stop_on_loss', stop_on_loss)

    def max_total_loss_percent(self) -> float:
        return self.get('max_total_loss_percent')
    
    def set_max_total_loss_percent(self, max_total_loss_percent: float):
        self.set('max_total_loss_percent', max_total_loss_percent)

    def cooldown_period_seconds(self) -> int:
        return self.get('cooldown_period_seconds')
    
    def set_cooldown_period_seconds(self, cooldown_period_seconds: int):
        self.set('cooldown_period_seconds', cooldown_period_seconds)

    def global_cooldown_period_seconds(self) -> int:
        return self.get('global_cooldown_period_seconds')
    
    def set_global_cooldown_period_seconds(self, global_cooldown_period_seconds: int):
        self.set('global_cooldown_period_seconds', global_cooldown_period_seconds)

    def global_disable_after_loss_percent(self) -> float:
        return self.get('global_disable_after_loss_percent')

    def set_global_disable_after_loss_percent(self, loss: float):
        self.set('global_disable_after_loss_percent', loss)

    def global_disable_after_loss_seconds(self) -> int:
        return self.get('global_disable_after_loss_seconds')
    
    def set_global_disable_after_loss_seconds(self, global_disable_after_loss_seconds: int):
        self.set('global_disable_after_loss_seconds', global_disable_after_loss_seconds)

    def disable_after_loss_seconds(self) -> int:
        return self.get('disable_after_loss_seconds')
    
    def set_disable_after_loss_seconds(self, disable_after_loss_seconds: int):
        self.set('disable_after_loss_seconds', disable_after_loss_seconds)

    def start_position_type(self) -> str:
        return self.get('start_position_type')
    
    def set_start_position_type(self, start_position_type: str):
        self.set('start_position_type', start_position_type)

    def end_position_type(self) -> str:
        return self.get('end_position_type')
    
    def set_end_position_type(self, end_position_type: str):
        self.set('end_position_type', end_position_type)

    def sell_all_on_stop(self) -> bool:
        return self.get('sell_all_on_stop')
    
    def set_sell_all_on_stop(self, sell_all_on_stop: bool):
        self.set('sell_all_on_stop', sell_all_on_stop)

    def position_open_buy_complete(self) -> bool:
        return self.get('position_open_buy_complete')
    
    def set_position_open_buy_complete(self, position_open_buy_complete: bool):
        self.set('position_open_buy_complete', position_open_buy_complete)

# temporary global configuration options used across all traders
    def global_disable_new_positions(self) -> bool:
        return self.get('tmp_global_disable_new_positions')
    
    def set_global_disable_new_positions(self, disable: bool):
        self.set('tmp_global_disable_new_positions', disable)

    def global_disable_new_positions_until_ts(self) -> int:
        return self.get('tmp_global_disable_new_positions_until_ts')
    
    def set_global_disable_new_positions_until_ts(self, ts: int):
        self.set('tmp_global_disable_new_positions_until_ts', ts)

    def global_current_balance_quote(self) -> float:
        return self.get('tmp_global_current_balance_quote')
    
    def set_global_current_balance_quote(self, balance: float):
        self.set('tmp_global_current_balance_quote', balance)

    def global_last_closed_position_profit(self):
        return self.get('tmp_global_last_closed_position_profit')

    def set_global_last_closed_position_profit(self, profit: float):
        self.set('tmp_global_last_closed_position_profit', profit)
