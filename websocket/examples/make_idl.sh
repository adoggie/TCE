#!/bin/sh
python ../../tce2js.py -i ../../idl/test.idl -o ./
python ../../tce2js.py -i ../../idl/sns.idl -o ./
rm -f parser.out parsetab.py
