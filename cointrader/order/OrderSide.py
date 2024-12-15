# Description: Enum for OrderSide
from enum import Enum

class OrderSide(Enum):
    UNKNOWN = 0
    NONE = 1
    BUY = 2
    SELL = 3