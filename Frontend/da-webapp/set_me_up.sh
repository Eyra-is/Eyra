#!/bin/bash

SDIR=$( dirname $( readlink -f $0 ) )

cd ${SDIR} && npm install && node_modules/grunt-cli/bin/grunt deploy
