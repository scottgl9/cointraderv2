# This file contains the SymbolInfo class which is used to store information about a trading pair

class SymbolInfo(object):
    initialized = False
    base_name = None
    quote_name = None
    price = 0.0
    base_min_size = 0
    base_step_size = 0.0
    quote_min_size = 0
    quote_step_size = 0.0
    is_currency_pair = False
    base_precision = 0
    quote_precision = 0
    orderTypes = None

    def __init__(self):
        self.initialized = False

    def load_from_dict(self, data):
        self.base = data['base']
        self.currency = data['currency']
        self.base_min_size = data['base_min_size']
        self.quote_min_size = data['quote_min_size']
        self.base_step_size = data['base_step_size']
        self.quote_step_size = data['quote_step_size']
        self.is_currency_pair = data['is_currency_pair']
        self.base_precision = data['base_precision']
        self.quote_precision = data['currency_precision']
        self.orderTypes = data['orderTypes']
        self.initialized = True

    def __dict__(self):
        return {
            'base': self.base,
            'currency': self.currency,
            'base_min_size': self.base_min_size,
            'quote_min_size': self.quote_min_size,
            'base_step_size': self.base_step_size,
            'quote_step_size': self.quote_step_size,
            'is_currency_pair': self.is_currency_pair,
            'base_precision': self.base_precision,
            'quote_precision': self.quote_precision,
            'orderTypes': self.orderTypes
        }

    def __repr__(self):
        return self.__dict__()
    
    def __str__(self):
        return str(self.__repr__())


    def get_order_types(self):
        return self.orderTypes
