# This file implements the OrderErrorReason enum class. This class is for the order error reason
from enum import Enum

class OrderErrorReason(Enum):
    UNKNOWN = "UNKNOWN"
    NONE = "NONE"
    INVALID_SYMBOL = "INVALID_SYMBOL"
    INSUFFIENT_BALANCE = "INSUFFICIENT_BALANCE"
    INVALID_PRICE = "INVALID_PRICE"
    INVALID_SIZE = "INVALID_SIZE"
    CLIENT_ERROR = "CLIENT_ERROR"

