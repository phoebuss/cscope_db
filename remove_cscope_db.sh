#!/usr/bin/env bash

CUR_DIR=`dirname $0`
find $CUR_DIR/{autoload,plugin,src,doc} -type f -name '*cscope_db*' | xargs rm
rm $0
