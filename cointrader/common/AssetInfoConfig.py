# handles all the configuration for all assets
# manages loading and saving asset info from a file
from .AssetInfo import AssetInfo
import os
import json

class AssetInfoConfig:
    filename = None
    def __init__(self, path):
        self._asset_info = {}
        self.path = path


    def file_exists(self):
        """
        Check if the file exists for asset info
        """
        if os.path.exists(self.path):
            return True
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

    def get_asset_info(self, symbol):
        pass

    def set_asset_info(self, symbol, asset_info: AssetInfo):
        pass
