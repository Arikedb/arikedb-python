#!/usr/bin/env bash

set -e

python -m grpc_tools.protoc -I=proto --python_out=. --grpc_python_out=. proto/arikedbpbuff.proto

cp arikedbpbuff_pb2.py arikedb/
cp arikedbpbuff_pb2_grpc.py arikedb/

sed -i 's/import arikedbpbuff_pb2 as arikedbpbuff__pb2/import arikedb.arikedbpbuff_pb2 as arikedbpbuff__pb2/g' arikedb/arikedbpbuff_pb2_grpc.py

rm -rf dist build

python3 setup.py sdist bdist_wheel

twine upload dist/*
