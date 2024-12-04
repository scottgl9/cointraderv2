# This file contains the AssetInfo class which is used to store information about an asset (currency)

class AssetInfo(object):
    initialized = False
    name = None
    min_size = 0
    step_size = 0.0
    precision = 0

    def __init__(self):
        self.initialized = False

    def load_from_dict(self, data):
        if 'name' in data.keys():
            self.name = data['name']
        self.min_size = data['min_size']
        self.step_size = data['step_size']
        self.precision = data['precision']
        self.initialized = True

    def to_dict(self):
        return {
            'name': self.name,
            'min_size': self.min_size,
            'step_size': self.step_size,
            'precision': self.precision
        }

    def __dict__(self):
        return self.to_dict()

    def __repr__(self):
        return self.__dict__()
    
    def __str__(self):
        return str(self.__repr__())
