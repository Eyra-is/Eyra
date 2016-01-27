#!/bin/bash

BDIR=$( dirname $( readlink -f $0 ) )
cd $BDIR && mysql -u root < erase_and_rewind.sql

