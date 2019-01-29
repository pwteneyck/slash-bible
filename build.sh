#!/usr/bin/env bash

rm function.zip
mkdir package
cd package
pip3 install boto3 --target .
zip -r9 ../function.zip .
cd ..
zip -g function.zip main.py
rm -rf package