# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: arike_utils.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'arike_utils.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11\x61rike_utils.proto\x12\x08\x61rike_pb*\xfa\x01\n\nStatusCode\x12\x06\n\x02OK\x10\x00\x12\x13\n\x0fLICENSE_EXPIRED\x10\x01\x12\x1b\n\x17LICENSE_LIMITS_EXCEEDED\x10\x02\x12\x13\n\x0fSESSION_EXPIRED\x10\x03\x12\x12\n\x0eINTERNAL_ERROR\x10\x04\x12\x10\n\x0cUNAUTHORIZED\x10\x05\x12\x13\n\x0fUNAUTHENTICATED\x10\x06\x12\x18\n\x14\x43OLLECTION_NOT_FOUND\x10\x07\x12\x16\n\x12VARIABLE_NOT_FOUND\x10\x08\x12\x13\n\x0fINVALID_REQUEST\x10\t\x12\x0e\n\nTYPE_ERROR\x10\n\x12\x0b\n\x07UNKNOWN\x10\x0b*\xb9\x02\n\x05\x45vent\x12\n\n\x06ON_SET\x10\x00\x12\r\n\tON_CHANGE\x10\x01\x12\x0b\n\x07ON_KEEP\x10\x02\x12\x0b\n\x07ON_RISE\x10\x03\x12\x0b\n\x07ON_FALL\x10\x04\x12\x10\n\x0cON_REACH_VAL\x10\x05\x12\r\n\tON_EQ_VAL\x10\x06\x12\x10\n\x0cON_LEAVE_VAL\x10\x07\x12\x0f\n\x0bON_DIFF_VAL\x10\x08\x12\x17\n\x13ON_CROSS_HIGH_LIMIT\x10\t\x12\x16\n\x12ON_CROSS_LOW_LIMIT\x10\n\x12\x16\n\x12ON_OVER_HIGH_LIMIT\x10\x0b\x12\x16\n\x12ON_UNDER_LOW_LIMIT\x10\x0c\x12\x12\n\x0eON_REACH_RANGE\x10\r\x12\x0f\n\x0bON_IN_RANGE\x10\x0e\x12\x12\n\x0eON_LEAVE_RANGE\x10\x0f\x12\x10\n\x0cON_OUT_RANGE\x10\x10*3\n\x07ValType\x12\x07\n\x03INT\x10\x00\x12\t\n\x05\x46LOAT\x10\x01\x12\n\n\x06STRING\x10\x02\x12\x08\n\x04\x42OOL\x10\x03\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'arike_utils_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_STATUSCODE']._serialized_start=32
  _globals['_STATUSCODE']._serialized_end=282
  _globals['_EVENT']._serialized_start=285
  _globals['_EVENT']._serialized_end=598
  _globals['_VALTYPE']._serialized_start=600
  _globals['_VALTYPE']._serialized_end=651
# @@protoc_insertion_point(module_scope)