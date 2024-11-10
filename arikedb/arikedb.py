from __future__ import annotations
from threading import Thread
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union

import grpc

from .common import ValueType, Status, VarEvent
from .arike_main_pb2_grpc import ArikedbRPCStub
from .arike_collection_pb2 import CollectionMeta, ListCollectionsRequest, CreateCollectionsRequest, DeleteCollectionsRequest
from .arike_ts_variable_pb2 import TsVariableMeta, ListVariablesRequest, CreateVariablesRequest, DeleteVariablesRequest, \
    SetVariablesRequest, GetVariablesRequest, SubscribeVariablesRequest, TsVarValue, VariableEvent
from .arike_stack_pb2 import StackMeta, ListStacksRequest, CreateStacksRequest, DeleteStacksRequest, \
    PutStacksRequest, PopStacksRequest, StackValue, StackNamesCount
from .arike_fifo_pb2 import FifoMeta, ListFifosRequest, CreateFifosRequest, DeleteFifosRequest, \
    PushFifosRequest, PullFifosRequest, FifoValue, FifoNamesCount
from .arike_sorted_list_pb2 import SortedListMeta, ListSortedListsRequest, CreateSortedListsRequest, DeleteSortedListsRequest, \
    InsertSortedListsRequest, BiggestSortedListsRequest, SmallestSortedListsRequest, SortedListValue, SortedListNamesCount
from .arike_auth_pb2 import AuthenticateRequest
from .arike_utils_pb2 import ValType


class TsVariable:
    def __init__(
        self,
        name: str,
        vtype: ValueType,
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
        return self.collection.ts_variables_set([(self.name, value, timestamp_ns)])

    def get(
        self
    ) -> Optional[Tuple[str, int, Union[int, float, str, bool]]]:
        val = self.collection.ts_variables_get([self.name])
        return val[0] if val else None


class Array:
    def __init__(
        self,
        name: str,
        vtype: ValueType,
        size: int,
        collection: Collection,
    ):
        self.name = name
        self.vtype = vtype
        self.size = size
        self.collection = collection


class Stack(Array):

    def put(
        self,
        values: Iterable[Union[int, float, str, bool]],
    ) -> Dict[str, List[str]]:
        return self.collection.stacks_put([(self.name, values)])

    def pop(
        self,
        n: Optional[int] = None
    ) -> Tuple[str, List[Union[int, float, str, bool]]]:
        return self.collection.stacks_pop([(self.name, n or 1)])[0]


class Fifo(Array):

    def push(
        self,
        values: Iterable[Union[int, float, str, bool]],
    ) -> Dict[str, List[str]]:
        return self.collection.fifos_push([(self.name, values)])

    def pull(
        self,
        n: Optional[int] = None
    ) -> Tuple[str, List[Union[int, float, str, bool]]]:
        return self.collection.fifos_pull([(self.name, n or 1)])[0]


class SortedList(Array):

    def insert(
        self,
        values: Iterable[Union[int, float, str, bool]],
    ) -> Dict[str, List[str]]:
        return self.collection.sorted_lists_insert([(self.name, values)])

    def biggest(
        self,
        n: Optional[int] = None,
        remove: bool = False
    ) -> Tuple[str, List[Union[int, float, str, bool]]]:
        return self.collection.sorted_lists_biggest([(self.name, n or 1)], remove)[0]

    def smallest(
        self,
        n: Optional[int] = None,
        remove: bool = False
    ) -> Tuple[str, List[Union[int, float, str, bool]]]:
        return self.collection.sorted_lists_smallest([(self.name, n or 1)], remove)[0]


class Collection:

    def __init__(
        self,
        name: str,
        client: Arikedb,
        **kwargs
    ):
        self.name = name
        self.client = client
        if not kwargs.get("dont_create"):
            client.create_collections([name])

    def ts_variables(
        self,
        pattern: Optional[str] = None
    ) -> List[TsVariable]:

        response = self.client._exec_request(
            self.client._stub.ListVariables,
            ListVariablesRequest,
            {"collection": self.name, "pattern": pattern}
        )
        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed to listing variables")
        return [TsVariable(v.name, ValueType(v.val_type), self) for v in response.variables]

    def ts_variable(
        self,
        name: str
    ) -> Optional[TsVariable]:

        ts_variables = self.ts_variables(name)
        return ts_variables[0] if len(ts_variables) > 0 else None

    def create_ts_variables(
        self,
        variables: Iterable[Tuple[str, ValueType]]
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
            if v.val_type == ValueType.Int.value:
                val_tup = (v.name, v.timestamp, v.int_value)
            elif v.val_type == ValueType.Float.value:
                val_tup = (v.name, v.timestamp, v.float_value)
            elif v.val_type == ValueType.String.value:
                val_tup = (v.name, v.timestamp, v.str_value)
            elif v.val_type == ValueType.Bool.value:
                val_tup = (v.name, v.timestamp, v.bool_value)
            else:
                continue
            values.append(val_tup)

        return values

    def variables_subscribe(
        self,
        names: Iterable[str],
        events: Iterable[VarEvent],
        callback: Callable,
        callback_args: Optional[tuple] = None,
        callback_kwargs: Optional[dict] = None,
        thread_kwargs: Optional[dict] = None,
    ) -> Thread:

        callback_args = callback_args or ()
        callback_kwargs = callback_kwargs or {}

        thread_kwargs = thread_kwargs or {}

        metadata = tuple() if not self.client._token else (('authorization', self.client._token),)

        def _wrapper():
            for response in self.client._stub.SubscribeVariables(
                SubscribeVariablesRequest(
                    collection=self.name,
                    names=names,
                    events=[
                        VariableEvent(
                            event=e.event.value,
                            str_value=e.str_value,
                            str_low_limit=e.str_low_limit,
                            str_high_limit=e.str_high_limit,
                            int_value=e.int_value,
                            int_low_limit=e.int_low_limit,
                            int_high_limit=e.int_high_limit,
                            float_value=e.float_value,
                            float_low_limit=e.float_low_limit,
                            float_high_limit=e.float_high_limit,
                            bool_value=e.bool_value,
                            bool_low_limit=e.bool_low_limit,
                            bool_high_limit=e.bool_high_limit
                        ) for e in events
                    ]
                ),
                metadata=metadata
            ):
                if response.val_type == ValType.INT:
                    value = response.int_value
                elif response.val_type == ValType.FLOAT:
                    value = response.float_value
                elif response.val_type == ValType.STRING:
                    value = response.str_value
                elif response.val_type == ValType.BOOL:
                    value = response.bool_value
                callback(
                    (response.name, response.timestamp, value),
                    *callback_args,
                    **callback_kwargs
                )

        t = Thread(target=_wrapper, **thread_kwargs)
        t.start()
        return t

    def stacks(
        self,
        pattern: Optional[str] = None
    ) -> List[Stack]:

        response = self.client._exec_request(
            self.client._stub.ListStacks,
            ListStacksRequest,
            {"collection": self.name, "pattern": pattern}
        )
        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed listing stacks")
        return [Stack(s.name, ValueType(s.val_type), s.max_size, self) for s in response.stacks]

    def stack(
        self,
        name: str
    ) -> Optional[Stack]:

        stacks = self.stacks(name)
        return stacks[0] if len(stacks) > 0 else None

    def create_stacks(
        self,
        stacks: Iterable[Tuple[str, ValueType, Optional[int]]]
    ) -> Dict[str, List[str]]:

        response = self.client._exec_request(
            self.client._stub.CreateStacks,
            CreateStacksRequest,
            {"collection": self.name,
             "stacks": [StackMeta(name=name, val_type=vtype.value, max_size=max_size) for name, vtype, max_size in stacks]}
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
    ) -> Dict:

        stk_values = []
        types_map = {
            int: "int_value",
            float: "float_value",
            str: "str_value",
            bool: "bool_value",
        }
        names = []
        for name, vals in values:
            if not vals:
                continue
            kw = {"name": name, types_map[type(vals[0])]: vals}
            stk_values.append(StackValue(**kw))
            names.append(name)

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
            "invalid_type": response.invalid_type,
            "non_inserted": {name: ni for name, ni in zip(names, response.non_inserted)}
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
            if v.val_type == ValueType.Int.value:
                val_tup = (v.name, v.int_value)
            elif v.val_type == ValueType.Float.value:
                val_tup = (v.name, v.float_value)
            elif v.val_type == ValueType.String.value:
                val_tup = (v.name, v.str_value)
            elif v.val_type == ValueType.Bool.value:
                val_tup = (v.name, v.bool_value)
            else:
                continue
            values.append(val_tup)

        return values

    def fifos(
        self,
        pattern: Optional[str] = None
    ) -> List[Fifo]:

        response = self.client._exec_request(
            self.client._stub.ListFifos,
            ListFifosRequest,
            {"collection": self.name, "pattern": pattern}
        )
        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed listing fifos")
        return [Fifo(s.name, ValueType(s.val_type), s.max_size, self) for s in response.fifos]

    def fifo(
        self,
        name: str
    ) -> Optional[Fifo]:

        fifos = self.fifos(name)
        return fifos[0] if len(fifos) > 0 else None

    def create_fifos(
        self,
        fifos: Iterable[Tuple[str, ValueType, Optional[int]]]
    ) -> Dict[str, List[str]]:

        response = self.client._exec_request(
            self.client._stub.CreateFifos,
            CreateFifosRequest,
            {"collection": self.name,
             "fifos": [FifoMeta(name=name, val_type=vtype.value, max_size=max_size) for name, vtype, max_size in fifos]}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed creating fifos")
        return {
            "already_exists": response.already_exists
        }

    def delete_fifos(
        self,
        names: Iterable[str]
    ) -> Dict[str, List[str]]:

        response = self.client._exec_request(
            self.client._stub.DeleteFifos,
            DeleteFifosRequest,
            {"collection": self.name, "names": names}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed deleting fifos")

        return {
            "not_found": response.not_found
        }

    def fifos_push(
        self,
        values: Iterable[Tuple[str, Iterable[Union[int, float, str, bool]]]]
    ) -> Dict:

        fifo_values = []
        types_map = {
            int: "int_value",
            float: "float_value",
            str: "str_value",
            bool: "bool_value",
        }
        names = []
        for name, vals in values:
            if not vals:
                continue
            kw = {"name": name, types_map[type(vals[0])]: vals}
            fifo_values.append(FifoValue(**kw))
            names.append(name)

        req_kw = {"collection": self.name, "values": fifo_values}
        response = self.client._exec_request(
            self.client._stub.PushFifos,
            PushFifosRequest,
            req_kw
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed pushing fifos")

        return {
            "not_found": response.not_found,
            "invalid_type": response.invalid_type,
            "non_inserted": {name: ni for name, ni in zip(names, response.non_inserted)}
        }

    def fifos_pull(
        self,
        names: Iterable[Union[str, Tuple[str, int]]],
    ) -> List[Tuple[str, List[Union[int, float, str, bool]]]]:

        names_counts = []
        for x in names:
            if isinstance(x, str):
                names_counts.append(FifoNamesCount(name=x, n=1))
            else:
                names_counts.append(FifoNamesCount(name=x[0], n=x[1]))

        response = self.client._exec_request(
            self.client._stub.PullFifos,
            PullFifosRequest,
            {"collection": self.name,
             "names_counts": names_counts}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed pulling fifos")

        values = []
        for v in response.values:
            if v.val_type == ValueType.Int.value:
                val_tup = (v.name, v.int_value)
            elif v.val_type == ValueType.Float.value:
                val_tup = (v.name, v.float_value)
            elif v.val_type == ValueType.String.value:
                val_tup = (v.name, v.str_value)
            elif v.val_type == ValueType.Bool.value:
                val_tup = (v.name, v.bool_value)
            else:
                continue
            values.append(val_tup)

        return values

    def sorted_lists(
        self,
        pattern: Optional[str] = None
    ) -> List[SortedList]:

        response = self.client._exec_request(
            self.client._stub.ListSortedLists,
            ListSortedListsRequest,
            {"collection": self.name, "pattern": pattern}
        )
        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed listing sorted lists")
        return [SortedList(s.name, ValueType(s.val_type), s.max_size, self) for s in response.sorted_lists]

    def sorted_list(
        self,
        name: str
    ) -> Optional[SortedList]:

        sorted_lists = self.sorted_lists(name)
        return sorted_lists[0] if len(sorted_lists) > 0 else None

    def create_sorted_lists(
        self,
        sorted_lists: Iterable[Tuple[str, ValueType, Optional[int]]]
    ) -> Dict[str, List[str]]:

        response = self.client._exec_request(
            self.client._stub.CreateSortedLists,
            CreateSortedListsRequest,
            {"collection": self.name,
             "sorted_lists": [SortedListMeta(name=name, val_type=vtype.value, max_size=max_size)
                              for name, vtype, max_size in sorted_lists]}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed creating sorted lists")
        return {
            "already_exists": response.already_exists
        }

    def delete_sorted_lists(
        self,
        names: Iterable[str]
    ) -> Dict[str, List[str]]:

        response = self.client._exec_request(
            self.client._stub.DeleteSortedLists,
            DeleteSortedListsRequest,
            {"collection": self.name, "names": names}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed deleting sorted lists")

        return {
            "not_found": response.not_found
        }

    def sorted_lists_insert(
        self,
        values: Iterable[Tuple[str, Iterable[Union[int, float, str, bool]]]]
    ) -> Dict:

        sorted_list_values = []
        types_map = {
            int: "int_value",
            float: "float_value",
            str: "str_value",
            bool: "bool_value",
        }
        names = []
        for name, vals in values:
            if not vals:
                continue
            kw = {"name": name, types_map[type(vals[0])]: vals}
            sorted_list_values.append(SortedListValue(**kw))
            names.append(name)

        req_kw = {"collection": self.name, "values": sorted_list_values}
        response = self.client._exec_request(
            self.client._stub.InsertSortedLists,
            InsertSortedListsRequest,
            req_kw
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed pushing sorted lists")

        return {
            "not_found": response.not_found,
            "invalid_type": response.invalid_type,
            "non_inserted": {name: ni for name, ni in zip(names, response.non_inserted)}
        }

    def sorted_lists_biggest(
        self,
        names: Iterable[Union[str, Tuple[str, int]]],
        remove: bool
    ) -> List[Tuple[str, List[Union[int, float, str, bool]]]]:

        names_counts = []
        for x in names:
            if isinstance(x, str):
                names_counts.append(SortedListNamesCount(name=x, n=1, remove=remove))
            else:
                names_counts.append(SortedListNamesCount(name=x[0], n=x[1], remove=remove))

        response = self.client._exec_request(
            self.client._stub.BiggestSortedLists,
            BiggestSortedListsRequest,
            {"collection": self.name,
             "names_counts": names_counts}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed reading biggest in sorted lists")

        values = []
        for v in response.values:
            if v.val_type == ValueType.Int.value:
                val_tup = (v.name, v.int_value)
            elif v.val_type == ValueType.Float.value:
                val_tup = (v.name, v.float_value)
            elif v.val_type == ValueType.String.value:
                val_tup = (v.name, v.str_value)
            elif v.val_type == ValueType.Bool.value:
                val_tup = (v.name, v.bool_value)
            else:
                continue
            values.append(val_tup)

        return values

    def sorted_lists_smallest(
        self,
        names: Iterable[Union[str, Tuple[str, int]]],
        remove: bool
    ) -> List[Tuple[str, List[Union[int, float, str, bool]]]]:

        names_counts = []
        for x in names:
            if isinstance(x, str):
                names_counts.append(SortedListNamesCount(name=x, n=1, remove=remove))
            else:
                names_counts.append(SortedListNamesCount(name=x[0], n=x[1], remove=remove))

        response = self.client._exec_request(
            self.client._stub.SmallestSortedLists,
            SmallestSortedListsRequest,
            {"collection": self.name,
             "names_counts": names_counts}
        )

        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed reading smallest in sorted lists")

        values = []
        for v in response.values:
            if v.val_type == ValueType.Int.value:
                val_tup = (v.name, v.int_value)
            elif v.val_type == ValueType.Float.value:
                val_tup = (v.name, v.float_value)
            elif v.val_type == ValueType.String.value:
                val_tup = (v.name, v.str_value)
            elif v.val_type == ValueType.Bool.value:
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
        username: Optional[str] = None,
        password: Optional[str] = None,
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
        self._token = None
        self._host = host
        self._port = port
        self._username = username
        self._password = password
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

        if self._username and self._password:
            response = self._exec_request(
                self._stub.Authenticate,
                AuthenticateRequest,
                {"username": self._username,
                 "password": self._password}
            )

            status = Status(response.status)
            if status != Status.Ok:
                raise status.as_exception("Authentication failed")

            self._token = response.token

        return self

    def disconnect(
        self
    ):
        self._channel.close()
        self._channel = None
        self._stub = None
        self._token = None

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

    def collections(
        self,
        pattern: Optional[str] = None
    ) -> List[Collection]:

        response = self._exec_request(
            self._stub.ListCollections,
            ListCollectionsRequest,
            {"pattern": pattern}
        )
        status = Status(response.status)
        if status != Status.Ok:
            raise status.as_exception("Failed listing collections")
        return [Collection(c.name, self, dont_create=True) for c in response.collections]

    def collection(
        self,
        name: str
    ) -> Optional[Collection]:

        collections = self.collections(pattern=name)
        return collections[0] if len(collections) > 0 else None

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
