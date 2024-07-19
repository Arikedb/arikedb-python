#!/usr/bin/env bash

set -e

python -m grpc_tools.protoc -I=proto --python_out=. --grpc_python_out=. proto/arikedbpbuff.proto

rm -rf dist build

python3 setup.py sdist bdist_wheel

twine upload dist/*
