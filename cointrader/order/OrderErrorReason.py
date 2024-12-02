# for errors in order status, determine reason
from enum import Enum

class OrderErrorReason(Enum):
    UNKNOWN = 0
    NONE = 1
    INVALID_SYMBOL = 2
    INSUFFIENT_BALANCE = 3
    INVALID_PRICE = 4
    INVALID_SIZE = 5
