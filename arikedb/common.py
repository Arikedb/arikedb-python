from enum import Enum
from typing import Optional


class TsVarType(Enum):
    TsInt = 0
    TsFloat = 1
    TsString = 2
    TsBool = 3


class StkType(Enum):
    StkInt = 4
    StkFloat = 5
    StkString = 6
    StkBool = 7


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
