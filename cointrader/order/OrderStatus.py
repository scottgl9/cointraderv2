# Description: Enum class for OrderStatus
from enum import Enum

class OrderStatus(Enum):
    UNKNOWN = 0
    NEW = 1
    PLACED = 2
    PARTIALLY_FILLED = 3
    FILLED = 4
    CANCELED = 5
    PENDING_CANCEL = 6
    REJECTED = 7
    EXPIRED = 8