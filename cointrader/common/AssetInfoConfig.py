# handles all the configuration for all symbols (trade pairs)
# manages loading and saving asset info from a file
from .AssetInfo import AssetInfo
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
import os
import json

class AssetInfoConfig:
    filename = None
    _exchange = None
    def __init__(self, exchange: TraderExchangeBase, path: str):
        self._asset_info_all = {}
        self._exchange = exchange
        self.path = path

    def file_exists(self) -> bool:
        """
        Check if the file exists for asset info
        """
        if os.path.exists(self.path):
            return True
        return False

    def empty(self) -> bool:
        """
        Check if the asset info is empty
        """
        if len(self._asset_info_all.keys()) == 0:
            return True
        return False

    def fetch(self) -> bool:
        """
        Fetch asset info from the exchange
        """
        try:
            info_all = self._exchange.info_ticker_query_all()
            for symbol, info in info_all.items():
                if not info.base_min_size or not info.base_step_size:
                    print(f"Missing base info for {symbol}")
                    continue
                base, quote = self._exchange.info_ticker_split(symbol)
                if base in self._asset_info_all.keys():
                    asset_info = self._asset_info_all[base]
                    if asset_info['min_size'] > info.base_min_size:
                        asset_info['min_size'] = info.base_min_size
                    if asset_info['step_size'] > info.base_step_size:
                        asset_info['step_size'] = info.base_step_size
                        asset_info['precision'] = info.base_precision
                else:
                    asset_info = {}
                    asset_info['min_size'] = info.base_min_size
                    asset_info['step_size'] = info.base_step_size
                    asset_info['precision'] = info.base_precision
                    self._asset_info_all[base] = asset_info

                if quote in self._asset_info_all.keys():
                    if asset_info['min_size'] > info.quote_min_size:
                        asset_info['min_size'] = info.quote_min_size
                    if asset_info['step_size'] > info.quote_step_size:
                        asset_info['step_size'] = info.quote_step_size
                        asset_info['precision'] = info.quote_precision
                else:
                    asset_info = {}
                    asset_info['min_size'] = info.quote_min_size
                    asset_info['step_size'] = info.quote_step_size
                    asset_info['precision'] = info.quote_precision
                    self._asset_info_all[quote] = asset_info
        except Exception as e:
            print(f"Error fetching asset info: {e}")
            return False

        return True

    def load(self) -> bool:
        """
        Load asset info from file
        """
        if not self.file_exists():
            return False
        try:
            with open(self.path, 'r') as f:
                self._asset_info_all = json.load(f)
        except Exception as e:
            print(f"Error loading asset info from {self.path}: {e}")
            return False

        return True

    def save(self) -> bool:
        """
        Save asset info to file
        """
        try:
            with open(self.path, 'w') as f:
                data = dict(sorted(self._asset_info_all.items()))
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving asset info to {self.path}: {e}")
            return False
        return True

    def get_asset_info(self, symbol) -> AssetInfo:
        if symbol not in self._asset_info_all.keys():
            print(f"Error: {symbol} not in asset info")
            return None
        info = AssetInfo()
        info.load_from_dict(self._asset_info_all[symbol])
        return info

    def set_asset_info(self, symbol, symbol_info: AssetInfo):
        self._asset_info_all[symbol]  = symbol_info.to_dict()
