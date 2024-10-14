#!/usr/bin/env bash

set -e

python -m grpc_tools.protoc -I=proto --python_out=. --grpc_python_out=. proto/arike_main.proto
python -m grpc_tools.protoc -I=proto --python_out=. proto/arike_auth.proto
python -m grpc_tools.protoc -I=proto --python_out=. proto/arike_collection.proto
python -m grpc_tools.protoc -I=proto --python_out=. proto/arike_ts_variable.proto
python -m grpc_tools.protoc -I=proto --python_out=. proto/arike_stack.proto
python -m grpc_tools.protoc -I=proto --python_out=. proto/arike_utils.proto

mv *_pb2.py arikedb/
mv *_pb2_grpc.py arikedb/

sed -i 's/import arike_/import arikedb.arike_/g' arikedb/arike_*_pb2*.py

# rm -rf dist build

# python3 setup.py sdist bdist_wheel

# twine upload dist/*
