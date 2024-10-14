from __future__ import annotations
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union

import grpc

from .common import TsVarType, StkType, Status
from .arike_main_pb2_grpc import ArikedbRPCStub
from .arike_collection_pb2 import CollectionMeta, ListCollectionsRequest, CreateCollectionsRequest, DeleteCollectionsRequest
from .arike_ts_variable_pb2 import TsVariableMeta, ListVariablesRequest, CreateVariablesRequest, DeleteVariablesRequest, \
    SetVariablesRequest, GetVariablesRequest, TsVarValue
from .arike_stack_pb2 import StackMeta, ListStacksRequest, CreateStacksRequest, DeleteStacksRequest, \
    PutStacksRequest, PopStacksRequest, StackValue, StackNamesCount


class TsVariable:
    def __init__(
        self,
        name: str,
        vtype: TsVarType,
        collection: Collection
    ):
        self.name = name
        self.vtype = vtype
        self.collection = collection

    def set(
        self,
        value: Union[int, float, str, bool],
        timestamp_ns: Optional[int] = None
    ) -> Dict[str, List[str]]:
        assert (isinstance(value, int) and self.vtype == TsVarType.TsInt) or \
               (isinstance(value, float) and self.vtype == TsVarType.TsFloat) or \
               (isinstance(value, str) and self.vtype == TsVarType.TsString) or \
               (isinstance(value, bool) and self.vtype == TsVarType.TsBool)

        return self.collection.ts_variables_set([(self.name, value, timestamp_ns)])

    def get(
        self
    ) -> Optional[Tuple[str, int, Union[int, float, str, bool]]]:
        val = self.collection.ts_variables_get([self.name])
        return val[0] if val else None


class Stack:
    def __init__(
        self,
        name: str,
        stktype: StkType,
        collection: Collection
    ):
        self.name = name
        self.stktype = stktype
        self.collection = collection


class Collection:
    def __init__(
        self,
        name: str,
        client: Arikedb
    ):
        self.name = name
        self.client = client

    def ts_variables(
        self
    ) -> List[TsVariable]:

        response = self.client._exec_request(
            self.client._stub.ListVariables,
            ListVariablesRequest,
            {"collection": self.name}
        )
        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed to listing variables")
        return [TsVariable(v.name, TsVarType(v.val_type), self) for v in response.variables]

    def create_ts_variables(
        self,
        variables: Iterable[Tuple[str, TsVarType]]
    ) -> Dict[str, List[str]]:

        response = self.client._exec_request(
            self.client._stub.CreateVariables,
            CreateVariablesRequest,
            {"collection": self.name,
             "variables": [TsVariableMeta(name=name, val_type=vt.value) for name, vt in variables]}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed creating variables")
        return {
            "already_exists": response.already_exists
        }

    def delete_ts_variables(
        self,
        names: Iterable[str]
    ) -> Dict[str, List[str]]:

        response = self.client._exec_request(
            self.client._stub.DeleteVariables,
            DeleteVariablesRequest,
            {"collection": self.name, "names": names}
        )
        if response.status != 0:
            raise Exception(f"Failed to list variables: {response.status}")

        return {
            "not_found": response.not_found
        }

    def ts_variables_set(
        self,
        values: Iterable[Tuple[str, Union[int, float, str, bool], Optional[int]]],
        timestamp_ns: Optional[int] = None
    ) -> Dict[str, List[str]]:

        var_values = []
        types_map = {
            int: "int_value",
            float: "float_value",
            str: "str_value",
            bool: "bool_value",
        }
        for x in values:
            kw = {"name": x[0], types_map[type(x[1])]: x[1]}
            if len(x) == 3:
                kw["timestamp"] = x[2]
            var_values.append(TsVarValue(**kw))

        req_kw = {"collection": self.name, "values": var_values}

        if timestamp_ns:
            req_kw["timestamp"] = timestamp_ns

        response = self.client._exec_request(
            self.client._stub.SetVariables,
            SetVariablesRequest,
            req_kw
        )

        status = Status(response.status)
        if status not in [Status.Ok, Status.VariableNotFound, Status.TypeError]:
            raise status.as_exception("Failed setting variables")

        return {
            "not_found": response.not_found,
            "invalid_type": response.invalid_type
        }

    def ts_variables_get(
        self,
        names: Iterable[str],
    ) -> List[Tuple[str, int, Union[int, float, str, bool]]]:

        response = self.client._exec_request(
            self.client._stub.GetVariables,
            GetVariablesRequest,
            {"collection": self.name, "names": names}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed getting variables")

        values = []
        for v in response.values:
            if v.val_type == TsVarType.TsInt.value:
                val_tup = (v.name, v.timestamp, v.int_value)
            elif v.val_type == TsVarType.TsFloat.value:
                val_tup = (v.name, v.timestamp, v.float_value)
            elif v.val_type == TsVarType.TsString.value:
                val_tup = (v.name, v.timestamp, v.str_value)
            elif v.val_type == TsVarType.TsBool.value:
                val_tup = (v.name, v.timestamp, v.bool_value)
            else:
                continue
            values.append(val_tup)

        return values

    def stacks(
        self
    ) -> List[Stack]:

        response = self.client._exec_request(
            self.client._stub.ListStacks,
            ListStacksRequest,
            {"collection": self.name}
        )
        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed listing stacks")
        return [Stack(s.name, StkType(s.val_type), self) for s in response.stacks]

    def create_stacks(
        self,
        stacks: Iterable[Tuple[str, StkType]]
    ) -> Dict[str, List[str]]:

        response = self.client._exec_request(
            self.client._stub.CreateStacks,
            CreateStacksRequest,
            {"collection": self.name,
             "stacks": [StackMeta(name=name, val_type=stk.value) for name, stk in stacks]}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed creating stacks")
        return {
            "already_exists": response.already_exists
        }

    def delete_stacks(
        self,
        names: Iterable[str]
    ) -> Dict[str, List[str]]:

        response = self.client._exec_request(
            self.client._stub.DeleteStacks,
            DeleteStacksRequest,
            {"collection": self.name, "names": names}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed deleting stacks")

        return {
            "not_found": response.not_found
        }

    def stacks_put(
        self,
        values: Iterable[Tuple[str, Iterable[Union[int, float, str, bool]]]]
    ) -> Dict[str, List[str]]:

        stk_values = []
        types_map = {
            int: "int_value",
            float: "float_value",
            str: "str_value",
            bool: "bool_value",
        }
        for name, vals in values:
            if not vals:
                continue
            kw = {"name": name, types_map[type(vals[0])]: vals}
            stk_values.append(StackValue(**kw))

        req_kw = {"collection": self.name, "values": stk_values}
        response = self.client._exec_request(
            self.client._stub.PutStacks,
            PutStacksRequest,
            req_kw
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed putting stacks")

        return {
            "not_found": response.not_found,
            "invalid_type": response.invalid_type
        }

    def stacks_pop(
        self,
        names: Iterable[Union[str, Tuple[str, int]]]
    ) -> List[Tuple[str, List[Union[int, float, str, bool]]]]:

        names_counts = []
        for x in names:
            if isinstance(x, str):
                names_counts.append(StackNamesCount(name=x, n=1))
            else:
                names_counts.append(StackNamesCount(name=x[0], n=x[1]))

        response = self.client._exec_request(
            self.client._stub.PopStacks,
            PopStacksRequest,
            {"collection": self.name,
             "names_counts": names_counts}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed popping stacks")

        values = []
        for v in response.values:
            if v.val_type == StkType.StkInt.value:
                val_tup = (v.name, v.int_value)
            elif v.val_type == StkType.StkFloat.value:
                val_tup = (v.name, v.float_value)
            elif v.val_type == StkType.StkString.value:
                val_tup = (v.name, v.str_value)
            elif v.val_type == StkType.StkBool.value:
                val_tup = (v.name, v.bool_value)
            else:
                continue
            values.append(val_tup)

        return values


class Arikedb:

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 6923,
        use_ssl_tls: bool = False,
        ca_path: Optional[str] = None,
        cert_path: Optional[str] = None,
        key_path: Optional[str] = None
    ):
        """RTDB Client constructor
        Args:
            host (str, optional): The hostname or IP address of the ArikeDB server. Defaults to "127.0.0.1".
            port (int, optional): The port number on which the ArikeDB server is listening. Defaults to 6923.
            use_ssl_tls (bool, optional): Whether to use SSL/TLS for the connection. Defaults to False.
            ca_path (Optional[str], optional): The file path to the Certificate Authority (CA) certificate.
                                               Required if use_ssl_tls is True. Defaults to None.
            cert_path (Optional[str], optional): The file path to the client certificate.
                                                 Required if use_ssl_tls is True and the server requires it.
                                                 Defaults to None.
            key_path (Optional[str], optional): The file path to the client private key.
                                                Required if use_ssl_tls is True and the server requires it.
                                                Defaults to None.
        """
        self._channel = None
        self._stub = None
        self._tOken = None
        self._host = host
        self._port = port
        self._use_ssl_tls = use_ssl_tls
        self._ca_path = ca_path
        self._cert_path = cert_path
        self._key_path = key_path

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self) -> Arikedb:
        """ Connect to the ArikeDB server.
        Returns:
            ArikedbClient: ArikedbClient instance.
        """

        url = f"{self._host}:{self._port}"

        _root_certificates: Optional[bytes] = None
        _private_key: Optional[bytes] = None
        _certificate_chain: Optional[bytes] = None

        if self._use_ssl_tls:
            if self._ca_path:
                with open(self._ca_path, 'rb') as f:
                    _root_certificates = f.read()
                if self._cert_path:
                    with open(self._cert_path, 'rb') as f:
                        _certificate_chain = f.read()
                if self._key_path:
                    with open(self._key_path, 'rb') as f:
                        _private_key = f.read()
                credentials = grpc.ssl_channel_credentials(root_certificates=_root_certificates,
                                                           private_key=_private_key,
                                                           certificate_chain=_certificate_chain)
            else:
                credentials = grpc.ssl_channel_credentials()
            self._channel = grpc.secure_channel(url, credentials)
        else:
            self._channel = grpc.insecure_channel(url)

        self._stub = ArikedbRPCStub(self._channel)

        return self

    def disconnect(
        self
    ):
        self._channel.close()
        self._channel = None
        self._stub = None
        self._tOken = None

    def _exec_request(
        self,
        method: Callable,
        request_class,
        request_kwargs: Optional[dict] = None,
        add_meta: bool = True
    ):
        request_kwargs = {} if request_kwargs is None else request_kwargs
        request = request_class(**request_kwargs)
        metadata = tuple() if (not add_meta or not self._tOken) else (('authorization', self._tOken),)
        response, call = method.with_call(request, metadata=metadata)

        resp_metadata = dict(call.initial_metadata())
        if "refresh_tOken" in resp_metadata:
            self._tOken = resp_metadata["refresh_tOken"]

        return response

    def collections(
        self
    ) -> List[Collection]:

        response = self._exec_request(
            self._stub.ListCollections,
            ListCollectionsRequest,
        )
        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed listing collections")
        return [Collection(c.name, self) for c in response.collections]

    def create_collections(
        self,
        names: Iterable[str]
    ) -> Dict[str, List[str]]:

        response = self._exec_request(
            self._stub.CreateCollections,
            CreateCollectionsRequest,
            {"collections": [CollectionMeta(name=name) for name in names]}
        )

        status = Status(response.status)
        if status not in [Status.Ok, Status.LicenseLimitsExceeded]:
            raise status.as_exception("Failed creating collections")

        return {
            "already_exists": response.already_exists,
            "license_exceeded": response.license_exceeded,
        }

    def delete_collections(
        self,
        names: Iterable[str]
    ) -> Dict[str, List[str]]:

        response = self._exec_request(
            self._stub.DeleteCollections,
            DeleteCollectionsRequest,
            {"names": names}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception(f"Failed to list collections: {response.status}")

        return {
            "not_found": response.not_found,
        }
