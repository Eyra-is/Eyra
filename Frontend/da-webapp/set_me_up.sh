#!/bin/bash
# Copyright 2016 Simon Klüpfel 
# Apache 2.0

SDIR=$( dirname $( readlink -f $0 ) )

cd ${SDIR} && npm install && node_modules/grunt-cli/bin/grunt deploy
