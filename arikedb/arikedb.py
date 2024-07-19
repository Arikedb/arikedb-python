from __future__ import annotations

from enum import Enum
from threading import Thread
from typing import Any, Callable, Iterable, List, Optional, Union
import grpc
from arikedbpbuff_pb2 import CreateCollectionsRequest
from arikedbpbuff_pb2 import DeleteCollectionsRequest
from arikedbpbuff_pb2 import ListCollectionsRequest
from arikedbpbuff_pb2 import CreateVariablesRequest
from arikedbpbuff_pb2 import DeleteVariablesRequest
from arikedbpbuff_pb2 import ListVariablesRequest
from arikedbpbuff_pb2 import SetVariablesRequest
from arikedbpbuff_pb2 import GetVariablesRequest
from arikedbpbuff_pb2 import SubscribeVariablesRequest
from arikedbpbuff_pb2 import AuthenticateRequest
from arikedbpbuff_pb2 import VariableMeta, CollectionMeta, VariableEvent
import arikedbpbuff_pb2_grpc


class Epoch(Enum):
    Second = 0
    Millisecond = 1
    Microsecond = 2
    Nanosecond = 3


class Event(Enum):
    OnSet = 0
    OnChange = 1
    OnRise = 2
    OnFall = 3
    OnValueReachVal = 4
    OnValueEqVal = 5
    OnValueLeaveVal = 6
    OnValueDiffVal = 7
    OnCrossHighLimit = 8
    OnCrossLowLimit = 9
    OnOverHighLimit = 10
    OnUnderLowLimit = 11
    OnValueReachRange = 12
    OnValueInRange = 13
    OnValueLeaveRange = 14
    OnValueOutRange = 15


class VariableType(Enum):
    I8 = 0
    I16 = 1
    I32 = 2
    I64 = 3
    I128 = 4
    U8 = 5
    U16 = 6
    U32 = 7
    U64 = 8
    U128 = 9
    F32 = 10
    F64 = 11
    STR = 12
    BOOL = 13


class Collection:
    def __init__(
        self,
        name: str
    ):
        self.name = name


class Variable:
    def __init__(
        self,
        name: str,
        vtype: VariableType,
        buffer_size: int
    ):
        self.name = name
        self.vtype = vtype
        self.buffer_size = buffer_size


class DataPoint:
    def __init__(
        self,
        name: str,
        vtype: VariableType,
        timestamp: int,
        epoch: Epoch,
        value
    ):
        self.name = name
        self.vtype = vtype
        self.timestamp = timestamp
        self.epoch = epoch
        self.value = value

    def tup(self):
        return (self.name, self.vtype, self.timestamp, self.epoch, self.value)


class StatusCode(Enum):
    OK = 0
    LICENSE_EXPIRED = 1
    LICENSE_LIMITS_EXCEEDED = 2
    SESSION_EXPIRED = 3
    INTERNAL_ERROR = 4
    UNAUTHORIZED = 5
    UNAUTHENTICATED = 6
    COLLECTION_NOT_FOUND = 7
    INVALID_REQUEST = 8


class Result:
    def __init__(
        self,
        status: StatusCode,
        collections: Optional[List[Collection]] = None,
        variables: Optional[List[Variable]] = None,
        data_points: Optional[List[DataPoint]] = None
    ):
        self.status = status
        self.collections = collections
        self.variables = variables
        self.data_points = data_points


class VarEvent:
    def __init__(
        self,
        event: Event,
        value: Optional[Union[float, int, bool, str]] = None,
        low_limit: Optional[float] = None,
        high_limit: Optional[float] = None
    ):
        self.event = event
        self.value = value
        self.low_limit = low_limit
        self.high_limit = high_limit


class ArikedbClient:

    def __init__(
        self,
    ):
        """RTDB Client constructor"""
        self._channel = None
        self._stub = None
        self._token = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(
        self,
        host: str = "127.0.0.1",
        port: int = 6923,
        use_ssl: bool = False
    ) -> ArikedbClient:

        url = f"{host}:{port}" if not use_ssl else f"https://{host}:{port}"
        self._channel = grpc.insecure_channel(url)
        self._stub = arikedbpbuff_pb2_grpc.ArikedbRPCStub(self._channel)

        return self

    def disconnect(
        self
    ):
        self._channel.close()
        self._channel = None
        self._stub = None
        self._token = None

    def list_collections(
        self
    ) -> Result:

        response = self._exec_request(
            self._stub.ListCollections,
            ListCollectionsRequest,
        )
        collections = [Collection(c.name) for c in response.collections]
        return Result(status=StatusCode(response.status), collections=collections)

    def create_collections(
        self,
        names: Iterable[Union[Collection, str, dict]]
    ) -> Result:

        collections = []

        for name in names:
            assert isinstance(name, (Collection, str, dict))
            if isinstance(name, dict):
                collections.append(CollectionMeta(name=name["name"]))
            elif isinstance(name, Collection):
                collections.append(CollectionMeta(name=name.name))
            else:
                collections.append(CollectionMeta(name=name))

        response = self._exec_request(
            self._stub.CreateCollections,
            CreateCollectionsRequest,
            {"collections": collections}
        )

        return Result(status=StatusCode(response.status))

    def delete_collections(
        self,
        names: Iterable[Union[Collection, str, dict]]
    ) -> Result:

        names_ = []
        for name in names:
            assert isinstance(name, (Collection, str, dict))
            if isinstance(name, dict):
                names_.append(name["name"])
            elif isinstance(name, Collection):
                names_.append(name.name)
            else:
                names_.append(name)

        response = self._exec_request(
            self._stub.DeleteCollections,
            DeleteCollectionsRequest,
            {"names": names_}
        )

        return Result(status=StatusCode(response.status))

    def list_variables(
        self,
        collection: Union[Collection, str, dict]
    ) -> Result:

        assert isinstance(collection, (Collection, str, dict))

        if isinstance(collection, dict):
            collection_name = collection["name"]
        elif isinstance(collection, Collection):
            collection_name = collection.name
        else:
            collection_name = collection

        response = self._exec_request(
            self._stub.ListVariables,
            ListVariablesRequest,
            {"collection": collection_name}
        )

        status = StatusCode(response.status)

        if status != StatusCode.OK:
            return Result(status=status)
        else:
            variables = [Variable(v.name, VariableType(v.vtype), v.buffer_size)
                         for v in response.variables]
            return Result(status=status, variables=variables)

    def create_variables(
        self,
        collection: Union[Collection, str, dict],
        variables: Iterable[Union[Variable, dict]]
    ) -> Result:

        assert isinstance(collection, (Collection, str, dict))

        variables_ = []
        for variable in variables:
            assert isinstance(variable, (Variable, dict))
            if isinstance(variable, dict):
                var = VariableMeta(
                    name=variable["name"],
                    vtype=variable["vtype"].value,
                    buffer_size=variable["buffer_size"]
                )
            else:
                var = VariableMeta(
                    name=variable.name,
                    vtype=variable.vtype.value,
                    buffer_size=variable.buffer_size
                )

            variables_.append(var)

        if isinstance(collection, dict):
            collection_name = collection["name"]
        elif isinstance(collection, Collection):
            collection_name = collection.name
        else:
            collection_name = collection

        response = self._exec_request(
            self._stub.CreateVariables,
            CreateVariablesRequest,
            {"collection": collection_name, "variables": variables_}
        )

        return Result(status=StatusCode(response.status))

    def delete_variables(
        self,
        collection: Union[Collection, str, dict],
        variables: Iterable[Union[Variable, dict, str]]
    ) -> Result:

        assert isinstance(collection, (Collection, str, dict))

        variables_ = []
        for variable in variables:
            assert isinstance(variable, (Variable, dict, str))
            if isinstance(variable, dict):
                variables_.append(variable["name"])
            elif isinstance(variable, Variable):
                variables_.append(variable.name)
            else:
                variables_.append(variable)

        if isinstance(collection, dict):
            collection_name = collection["name"]
        elif isinstance(collection, Collection):
            collection_name = collection.name
        else:
            collection_name = collection

        response = self._exec_request(
            self._stub.DeleteVariables,
            DeleteVariablesRequest,
            {"collection": collection_name, "names": variables_}
        )

        return Result(status=StatusCode(response.status))

    def set_variables(
        self,
        collection: Union[Collection, str, dict],
        variables: Iterable[Union[Variable, dict, str]],
        timestamp: int,
        values: Iterable[Union[int, float, str, bool]],
        epoch: Epoch,
    ) -> Result:

        assert isinstance(collection, (Collection, str, dict))

        var_names = []
        for variable in variables:
            assert isinstance(variable, (Variable, dict, str))
            if isinstance(variable, dict):
                var_names.append(variable["name"])
            elif isinstance(variable, Variable):
                var_names.append(variable.name)
            else:
                var_names.append(variable)

        if isinstance(collection, dict):
            collection_name = collection["name"]
        elif isinstance(collection, Collection):
            collection_name = collection.name
        else:
            collection_name = collection

        response = self._exec_request(
            self._stub.SetVariables,
            SetVariablesRequest,
            {
                "collection": collection_name,
                "names": var_names,
                "values": [str(v) for v in values],
                "timestamp": str(timestamp),
                "epoch": epoch.value
            }
        )

        return Result(status=StatusCode(response.status))

    def get_variables(
        self,
        collection: Union[Collection, str, dict],
        variables: Iterable[Union[Variable, dict, str]],
        epoch: Epoch,
        derived_order: int = 0
    ) -> Result:

        assert isinstance(collection, (Collection, str, dict))
        assert derived_order >= 0

        var_names = []
        for variable in variables:
            assert isinstance(variable, (Variable, dict, str))
            if isinstance(variable, dict):
                var_names.append(variable["name"])
            elif isinstance(variable, Variable):
                var_names.append(variable.name)
            else:
                var_names.append(variable)

        if isinstance(collection, dict):
            collection_name = collection["name"]
        elif isinstance(collection, Collection):
            collection_name = collection.name
        else:
            collection_name = collection

        response = self._exec_request(
            self._stub.GetVariables,
            GetVariablesRequest,
            {
                "collection": collection_name,
                "names": var_names,
                "derived_order": derived_order,
                "epoch": epoch.value
            }
        )

        status = StatusCode(response.status)

        if status != StatusCode.OK:
            return Result(status=status)
        else:
            return Result(
                status=status,
                data_points=[
                    DataPoint(
                        name=v.name,
                        vtype=VariableType(v.vtype),
                        timestamp=int(v.timestamp),
                        epoch=epoch,
                        value=self._cast_value(v.value, VariableType(v.vtype))
                    ) for v in response.points
                ]
            )

    def subscribe_variables(
        self,
        collection: Union[Collection, str, dict],
        variables: Iterable[Union[Variable, dict, str]],
        events: Iterable[VarEvent],
        callback: Callable[[DataPoint, Any], Any],
        callback_args: Optional[tuple] = None,
        callback_kwargs: Optional[dict] = None,
        thread_kwargs: Optional[dict] = None,
    ) -> Thread:

        assert isinstance(collection, (Collection, str, dict))
        callback_args = callback_args or ()
        callback_kwargs = callback_kwargs or {}

        thread_kwargs = thread_kwargs or {}

        var_names = []
        for variable in variables:
            assert isinstance(variable, (Variable, dict, str))
            if isinstance(variable, dict):
                var_names.append(variable["name"])
            elif isinstance(variable, Variable):
                var_names.append(variable.name)
            else:
                var_names.append(variable)

        if isinstance(collection, dict):
            collection_name = collection["name"]
        elif isinstance(collection, Collection):
            collection_name = collection.name
        else:
            collection_name = collection

        metadata = tuple() if not self._token else (('authorization', self._token),)

        def _wrapper():
            for response in self._stub.SubscribeVariables(
                SubscribeVariablesRequest(
                    collection=collection_name,
                    names=var_names,
                    events=[
                        VariableEvent(
                            event=e.event.value,
                            value=str(e.value),
                            low_limit=str(e.low_limit),
                            high_limit=str(e.high_limit)
                        ) for e in events
                    ]
                ),
                metadata=metadata
            ):
                callback(
                    DataPoint(
                        name=response.name,
                        vtype=VariableType(response.vtype),
                        timestamp=int(response.timestamp),
                        epoch=Epoch(response.epoch),
                        value=self._cast_value(response.value, VariableType(response.vtype))
                    ),
                    *callback_args,
                    **callback_kwargs
                )

        t = Thread(target=_wrapper, **thread_kwargs)
        t.start()
        return t

    def authenticate(
        self,
        username: str,
        password: str
    ) -> Result:

        response = self._stub.Authenticate(
            AuthenticateRequest(
                username=username,
                password=password
            )
        )

        if response.status != StatusCode.OK.value:
            self._token = None
            return Result(status=StatusCode(response.status))
        else:
            self._token = response.token
            return Result(status=StatusCode(response.status))

    def _exec_request(
        self,
        method: Callable,
        request_class,
        request_kwargs: Optional[dict] = None,
        add_meta: bool = True
    ):
        request_kwargs = {} if request_kwargs is None else request_kwargs
        request = request_class(**request_kwargs)
        metadata = tuple() if (not add_meta or not self._token) else (('authorization', self._token),)
        response, call = method.with_call(request, metadata=metadata)

        resp_metadata = dict(call.initial_metadata())
        if "refresh_token" in resp_metadata:
            self._token = resp_metadata["refresh_token"]

        return response

    def _cast_value(self, value: str, vtype: VariableType):
        if vtype == VariableType.BOOL:
            return bool(int(value))
        elif vtype in [
            VariableType.I8,
            VariableType.I16,
            VariableType.I32,
            VariableType.I64,
            VariableType.I128,
            VariableType.U8,
            VariableType.U16,
            VariableType.U32,
            VariableType.U64,
            VariableType.U128
        ]:
            return int(value)
        elif vtype in [
            VariableType.F32,
            VariableType.F64
        ]:
            return float(value)
        elif vtype == VariableType.STR:
            return value
