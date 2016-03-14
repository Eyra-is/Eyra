#!/bin/bash

BDIR=$( dirname $( readlink -f $0 ) )
cd $BDIR && mysql -u root -p < erase_and_rewind.sql

