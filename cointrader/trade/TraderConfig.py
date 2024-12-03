import os
import json

# Example of a trade config
DEFAULT_TRADE_CONFIG = {
    'max_positions': 1,
    'quote_currency': 'USD',
    'max_position_quote_size': 25.0,
    'strategy': 'Default',
    'trade_symbols': ['BTC-USD', 'ETH-USD', 'SOL-USD'],
    'stop_loss_percent': 5.0,
    'trailing_stop_loss': False,
    'min_take_profit_percent': 5.0,
    'stop_on_loss': True,
    'max_total_loss_percent': 10.0,
    'cooldown_period_seconds': 60,
    'start_position_type': 'MARKET',
    'end_position_type': 'MARKET',
    'sell_all_on_stop': False
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
