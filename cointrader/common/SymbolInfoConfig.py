# handles all the configuration for all symbols (trade pairs)
# manages loading and saving asset info from a file
from .SymbolInfo import SymbolInfo
from cointrader.client.TraderClientBase import TraderClientBase
import os
import json

class SymbolInfoConfig:
    filename = None
    _client = None
    def __init__(self, client: TraderClientBase, path: str):
        self._symbol_info_all = {}
        self._client = client
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
        Check if the symbol info is empty
        """
        if len(self._symbol_info_all.keys()) == 0:
            return True
        return False

    def fetch(self) -> bool:
        """
        Fetch symbol info from the exchange
        """
        try:
            info_all = self._client.info_ticker_query_all()
            for symbol, info in info_all.items():
                self._symbol_info_all[symbol] = info.to_dict()
        except Exception as e:
            print(f"Error fetching symbol info: {e}")
            return False

        return True

    def load(self) -> bool:
        """
        Load symbol info from file
        """
        if not self.file_exists():
            return False
        try:
            with open(self.path, 'r') as f:
                self._symbol_info_all = json.load(f)
        except Exception as e:
            print(f"Error loading asset info from {self.path}: {e}")
            return False

        return True

    def save(self) -> bool:
        """
        Save symbol info to file
        """
        try:
            with open(self.path, 'w') as f:
                data = dict(sorted(self._symbol_info_all.items()))
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving asset info to {self.path}: {e}")
            return False
        return True

    def get_symbol_info(self, symbol) -> SymbolInfo:
        if symbol not in self._symbol_info_all.keys():
            return None
        info = SymbolInfo()
        info.load_from_dict(self._symbol_info_all[symbol])
        return info

    def set_symbol_info(self, symbol, symbol_info: SymbolInfo):
        self._symbol_info_all[symbol]  = symbol_info.to_dict()
