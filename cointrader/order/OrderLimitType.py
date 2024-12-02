from enum import Enum

class OrderLimitType(Enum):
    UNKNOWN = 0
    GTC = 1
    IOC = 2
    FOK = 3
    DAY = 4
    GTD = 5
