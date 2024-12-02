# Description: Enum for order types
from enum import Enum

class OrderType(Enum):
    UNKNOWN = 0
    LIMIT = 1
    MARKET = 2
    STOP_LOSS = 3
    STOP_LOSS_LIMIT = 4
    TAKE_PROFIT = 5
