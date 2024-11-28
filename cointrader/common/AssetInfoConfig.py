# handles all the configuration for all assets
# manages loading and saving asset info from a file
from .AssetInfo import AssetInfo
import os
import json

class AssetInfoConfig:
    filename = None
    _client = None
    def __init__(self, client, path):
        self._asset_info = {}
        self._client = client
        self.path = path


    def file_exists(self) -> bool:
        """
        Check if the file exists for asset info
        """
        if os.path.exists(self.path):
            return True
        return False

    def fetch(self) -> bool:
        return False

    def load(self) -> bool:
        if not self.file_exists():
            return False
        try:
            with open(self.path, 'r') as f:
                self._asset_info = json.load(f)
        except Exception as e:
            print(f"Error loading asset info from {self.path}: {e}")
            return False

        return True

    def save(self) -> bool:
        try:
            with open(self.path, 'w') as f:
                json.dump(self._asset_info, f)
        except Exception as e:
            print(f"Error saving asset info to {self.path}: {e}")
            return False
        return True

    def get_asset_info(self, symbol) -> AssetInfo:
        if symbol not in self._asset_info.keys():
            return None
        info = AssetInfo()
        info.load_dict(self._asset_info[symbol])
        return info

    def set_asset_info(self, symbol, asset_info: AssetInfo):
        self._asset_info[symbol] = dict(asset_info)
