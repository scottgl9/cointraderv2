# This file is used to define an OrderSide enum class. This class is for the order side
from enum import Enum

class OrderSide(Enum):
    UNKNOWN = "UNKNOWN"
    NONE = "NONE"
    BUY = "BUY"
    SELL = "SELL"
