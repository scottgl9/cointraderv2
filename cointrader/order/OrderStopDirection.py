# This file implements the OrderStopDirection enum class. This class is for the order direction regarding stop loss orders
from enum import Enum

class OrderStopDirection(Enum):
    UNKNOWN = "UNKNOWN"
    NONE = "NONE"
    ABOVE = "ABOVE"
    BELOW = "BELOW"
