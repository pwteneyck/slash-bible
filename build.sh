#!/usr/bin/env bash

rm function.zip
mkdir build
cd build
pip3 install boto3 --target .
zip -r9 ../function.zip .
cd ..
zip -g function.zip src/main.py
rm -rf build