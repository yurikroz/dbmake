#!/bin/bash

BASEDIR=$(dirname $0)
python $BASEDIR/../dbmake/dbmake.py $*
