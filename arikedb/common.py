from enum import Enum
from typing import Optional


class ValueType(Enum):
    Int = 0
    Float = 1
    String = 2
    Bool = 3


class Event(Enum):
    OnSet = 0
    OnChange = 1
    OnKeep = 2
    OnRise = 3
    OnFall = 4
    OnValueReachVal = 5
    OnValueEqVal = 6
    OnValueLeaveVal = 7
    OnValueDiffVal = 8
    OnCrossHighLimit = 9
    OnCrossLowLimit = 10
    OnOverHighLimit = 11
    OnUnderLowLimit = 12
    OnValueReachRange = 13
    OnValueInRange = 14
    OnValueLeaveRange = 15
    OnValueOutRange = 16


class Status(Enum):
    Ok = 0
    LicenseExpired = 1
    LicenseLimitsExceeded = 2
    SessionExpired = 3
    InternalError = 4
    Unauthorized = 5
    Unauthenticated = 6
    CollectionNotFound = 7
    VariableNotFound = 8
    InvalidRequest = 9
    TypeError = 10
    Unknown = 11

    @property
    def as_exception(self) -> Optional[Exception]:
        match self.value:
            case 0:
                return None
            case 1:
                return LicenseExpired
            case 3:
                return SessionExpired
            case 4:
                return InternalError
            case 5:
                return Unauthorized
            case 6:
                return Unauthenticated
            case 7:
                return CollectionNotFound
            case 8:
                return VariableNotFound
            case 9:
                return InvalidRequest
            case 10:
                return TypeError
            case 11:
                return Unknown


class VarEvent:
    def __init__(
        self,
        event: Event,
        str_value: Optional[str] = None,
        str_low_limit: Optional[str] = None,
        str_high_limit: Optional[str] = None,
        int_value: Optional[int] = None,
        int_low_limit: Optional[int] = None,
        int_high_limit: Optional[int] = None,
        float_value: Optional[float] = None,
        float_low_limit: Optional[float] = None,
        float_high_limit: Optional[float] = None,
        bool_value: Optional[bool] = None,
        bool_low_limit: Optional[bool] = None,
        bool_high_limit: Optional[bool] = None,
    ):
        self.event = event
        self.str_value = str_value
        self.str_low_limit = str_low_limit
        self.str_high_limit = str_high_limit
        self.int_value = int_value
        self.int_low_limit = int_low_limit
        self.int_high_limit = int_high_limit
        self.float_value = float_value
        self.float_low_limit = float_low_limit
        self.float_high_limit = float_high_limit
        self.bool_value = bool_value
        self.bool_low_limit = bool_low_limit
        self.bool_high_limit = bool_high_limit


class LicenseExpired(Exception):
    pass


class SessionExpired(Exception):
    pass


class InternalError(Exception):
    pass


class Unauthorized(Exception):
    pass


class Unauthenticated(Exception):
    pass


class CollectionNotFound(Exception):
    pass


class VariableNotFound(Exception):
    pass


class InvalidRequest(Exception):
    pass


class TypeError(Exception):
    pass


class Unknown(Exception):
    pass
