from enum import Enum
from typing import Optional, Union


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
        value: Optional[Union[int, float, str, bool]] = None,
        low_limit: Optional[Union[int, float, str, bool]] = None,
        high_limit: Optional[Union[int, float, str, bool]] = None,
    ):
        v_class = type(value)
        ll_class = type(low_limit)
        hl_class = type(high_limit)

        self.event = event
        self.str_value = value if v_class == str else None
        self.str_low_limit = low_limit if ll_class == str else None
        self.str_high_limit = high_limit if hl_class == str else None
        self.int_value = value if v_class == int else None
        self.int_low_limit = low_limit if ll_class == int else None
        self.int_high_limit = high_limit if hl_class == int else None
        self.float_value = value if v_class == float else None
        self.float_low_limit = low_limit if ll_class == float else None
        self.float_high_limit = high_limit if hl_class == float else None
        self.bool_value = value if v_class == bool else None
        self.bool_low_limit = low_limit if ll_class == bool else None
        self.bool_high_limit = high_limit if hl_class == bool else None


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
