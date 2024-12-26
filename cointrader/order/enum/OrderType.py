# This file implements the OrderType enum class. This class is for the order type
from enum import Enum

class OrderType(Enum):
    UNKNOWN = "UNKNOWN"
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    STATUS = "STATUS"
    CANCEL = "CANCEL"
