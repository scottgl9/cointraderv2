import os
import json

# Example of a trade config
DEFAULT_TRADE_CONFIG = {
    'simulate': True,                      # Simulate trading without making real trades
    'verbose': False,                      # Print verbose output
    'max_positions': 1,                    # Maximum number of positions to hold per symbol
    'quote_currency': 'USD',               # Currency to use for trading
    'max_position_quote_size': 25.0,       # Maximum size of a position in quote currency
    'strategy': 'SignalStrength',          # Strategy to use for trading
    'trade_symbols': ['BTC-USD', 'ETH-USD', 'SOL-USD'],
    'stop_loss_percent': 5.0,              # percent stop loss to set under the buy price
    'stop_loss_limit_order_percent': 0.1,  # percent to set the stop loss above or below the limit price
    'limit_order_percent': 0.2,            # percent to set the limit price above or below the current price
    'cancel_order_percent': 3.0,           # of price movement away from order before order gets cancelled (limit and stop loss limit orders)
    'trailing_stop_loss': False,           # stop loss follows the price up
    'min_take_profit_percent': 0.5,        # minimum percent profit to take
    'stop_on_loss': True,                  # Stop trading bot after a loss
    'max_total_loss_percent': 10.0,        # Maximum total loss percent before stopping the bot
    'cooldown_period_seconds': 3600,       # cooldown period after entering a position before opening another
    'disable_after_loss_seconds': 86400,   # Disable trading for this many seconds after a loss
    'start_position_type': 'LIMIT',        # Type of order to open a position (MARKET, LIMIT, STOP_LOSS_LIMIT)
    'end_position_type': 'LIMIT',          # Type of order to open a position (MARKET, LIMIT, STOP_LOSS_LIMIT)
    'sell_all_on_stop': False              # sell all open positions when the bot stops
}

class TraderConfig(object):
    def __init__(self, path : str):
        self._path = path
        self._config = DEFAULT_TRADE_CONFIG

    def path(self) -> str:
        return self._path

    def get_config(self):
        return self._config

    def config_file_exists(self) -> bool:
        if os.path.exists(self._path):
            return True
        return False

    def load_config(self) -> bool:
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
                print(self._config)
                json.dump(self._config, f, indent=4)
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
        self.save_config()

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
    
    def verbose(self):
        return self.get('verbose')

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

    def trade_symbols(self) -> dict:
        return self.get('trade_symbols')
    
    def set_trade_symbols(self, trade_symbols: dict):
        self.set('trade_symbols', trade_symbols)

    def stop_loss_percent(self) -> float:
        return self.get('stop_loss_percent')
    
    def set_stop_loss_percent(self, stop_loss_percent: float):
        self.set('stop_loss_percent', stop_loss_percent)

    def stop_loss_limit_order_percent(self) -> float:
        return self.get('stop_loss_limit_order_percent')
    
    def set_stop_loss_limit_order_percent(self, stop_loss_limit_order_percent: float):
        self.set('stop_loss_limit_order_percent', stop_loss_limit_order_percent)

    def limit_order_percent(self) -> float:
        return self.get('limit_order_percent')
    
    def set_limit_order_percent(self, limit_order_percent: float):
        self.set('limit_order_percent', limit_order_percent)

    def cancel_order_percent(self) -> float:
        return self.get('cancel_order_percent')
    
    def set_cancel_order_percent(self, cancel_order_percent: float):
        self.set('cancel_order_percent', cancel_order_percent)

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
