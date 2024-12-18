# This file implements the OrderLimitType enum class. This class is for the order limit type
from enum import Enum

class OrderLimitType(Enum):
    UNKNOWN = "UNKNOWN"
    GTC = "GTC"                 # Good Till Cancelled
    IOC = "IOC"                 # Immediate Or Cancel
    FOK = "FOK"                 # Fill Or Kill
    DAY = "DAY"                 # Day
    GTD = "GTD"                 # Good Till Date
