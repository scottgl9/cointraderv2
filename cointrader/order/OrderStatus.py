# This file implements the OrderStatus enum class. This class is for the order status
from enum import Enum

class OrderStatus(Enum):
    UNKNOWN = "UNKNOWN"
    NEW = "NEW"
    PLACED = "PLACED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    PENDING_CANCEL = "PENDING_CANCEL"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ERROR = "ERROR"
