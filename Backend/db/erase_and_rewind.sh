#!/bin/bash
# Copyright 2016 Simon Klüpfel 
# Apache 2.0

BDIR=$( dirname $( readlink -f $0 ) )
cd $BDIR && mysql -u root -p < erase_and_rewind.sql

