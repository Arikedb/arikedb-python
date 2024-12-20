# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: arike_fifo.proto
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
    'arike_fifo.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import arikedb.arike_utils_pb2 as arike__utils__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10\x61rike_fifo.proto\x12\x08\x61rike_pb\x1a\x11\x61rike_utils.proto\"a\n\x08\x46ifoMeta\x12\x0c\n\x04name\x18\x01 \x01(\t\x12#\n\x08val_type\x18\x02 \x01(\x0e\x32\x11.arike_pb.ValType\x12\x15\n\x08max_size\x18\x03 \x01(\x04H\x00\x88\x01\x01\x42\x0b\n\t_max_size\")\n\x0e\x46ifoNamesCount\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\t\n\x01n\x18\x02 \x01(\r\"\x9f\x01\n\tFifoValue\x12\x0c\n\x04name\x18\x01 \x01(\t\x12(\n\x08val_type\x18\x02 \x01(\x0e\x32\x11.arike_pb.ValTypeH\x00\x88\x01\x01\x12\x11\n\tint_value\x18\x03 \x03(\x03\x12\x13\n\x0b\x66loat_value\x18\x04 \x03(\x01\x12\x11\n\tstr_value\x18\x05 \x03(\t\x12\x12\n\nbool_value\x18\x06 \x03(\x08\x42\x0b\n\t_val_type\"K\n\x12\x43reateFifosRequest\x12\x12\n\ncollection\x18\x01 \x01(\t\x12!\n\x05\x66ifos\x18\x02 \x03(\x0b\x32\x12.arike_pb.FifoMeta\"S\n\x13\x43reateFifosResponse\x12$\n\x06status\x18\x01 \x01(\x0e\x32\x14.arike_pb.StatusCode\x12\x16\n\x0e\x61lready_exists\x18\x02 \x03(\t\"7\n\x12\x44\x65leteFifosRequest\x12\x12\n\ncollection\x18\x01 \x01(\t\x12\r\n\x05names\x18\x02 \x03(\t\"N\n\x13\x44\x65leteFifosResponse\x12$\n\x06status\x18\x01 \x01(\x0e\x32\x14.arike_pb.StatusCode\x12\x11\n\tnot_found\x18\x02 \x03(\t\"H\n\x10ListFifosRequest\x12\x12\n\ncollection\x18\x01 \x01(\t\x12\x14\n\x07pattern\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\n\n\x08_pattern\"\\\n\x11ListFifosResponse\x12$\n\x06status\x18\x01 \x01(\x0e\x32\x14.arike_pb.StatusCode\x12!\n\x05\x66ifos\x18\x02 \x03(\x0b\x32\x12.arike_pb.FifoMeta\"K\n\x10PushFifosRequest\x12\x12\n\ncollection\x18\x01 \x01(\t\x12#\n\x06values\x18\x02 \x03(\x0b\x32\x13.arike_pb.FifoValue\"x\n\x11PushFifosResponse\x12$\n\x06status\x18\x01 \x01(\x0e\x32\x14.arike_pb.StatusCode\x12\x11\n\tnot_found\x18\x02 \x03(\t\x12\x14\n\x0cinvalid_type\x18\x03 \x03(\t\x12\x14\n\x0cnon_inserted\x18\x04 \x03(\x04\"V\n\x10PullFifosRequest\x12\x12\n\ncollection\x18\x01 \x01(\t\x12.\n\x0cnames_counts\x18\x02 \x03(\x0b\x32\x18.arike_pb.FifoNamesCount\"^\n\x11PullFifosResponse\x12$\n\x06status\x18\x01 \x01(\x0e\x32\x14.arike_pb.StatusCode\x12#\n\x06values\x18\x02 \x03(\x0b\x32\x13.arike_pb.FifoValueb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'arike_fifo_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_FIFOMETA']._serialized_start=49
  _globals['_FIFOMETA']._serialized_end=146
  _globals['_FIFONAMESCOUNT']._serialized_start=148
  _globals['_FIFONAMESCOUNT']._serialized_end=189
  _globals['_FIFOVALUE']._serialized_start=192
  _globals['_FIFOVALUE']._serialized_end=351
  _globals['_CREATEFIFOSREQUEST']._serialized_start=353
  _globals['_CREATEFIFOSREQUEST']._serialized_end=428
  _globals['_CREATEFIFOSRESPONSE']._serialized_start=430
  _globals['_CREATEFIFOSRESPONSE']._serialized_end=513
  _globals['_DELETEFIFOSREQUEST']._serialized_start=515
  _globals['_DELETEFIFOSREQUEST']._serialized_end=570
  _globals['_DELETEFIFOSRESPONSE']._serialized_start=572
  _globals['_DELETEFIFOSRESPONSE']._serialized_end=650
  _globals['_LISTFIFOSREQUEST']._serialized_start=652
  _globals['_LISTFIFOSREQUEST']._serialized_end=724
  _globals['_LISTFIFOSRESPONSE']._serialized_start=726
  _globals['_LISTFIFOSRESPONSE']._serialized_end=818
  _globals['_PUSHFIFOSREQUEST']._serialized_start=820
  _globals['_PUSHFIFOSREQUEST']._serialized_end=895
  _globals['_PUSHFIFOSRESPONSE']._serialized_start=897
  _globals['_PUSHFIFOSRESPONSE']._serialized_end=1017
  _globals['_PULLFIFOSREQUEST']._serialized_start=1019
  _globals['_PULLFIFOSREQUEST']._serialized_end=1105
  _globals['_PULLFIFOSRESPONSE']._serialized_start=1107
  _globals['_PULLFIFOSRESPONSE']._serialized_end=1201
# @@protoc_insertion_point(module_scope)
