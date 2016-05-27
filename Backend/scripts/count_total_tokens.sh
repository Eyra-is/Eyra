#!/bin/bash
# Copyright 2016 Matthias Petursson
# Apache 2.0

# Get the script directory
SDIR=$( dirname $( readlink -f $0 ) )
cd "$SDIR"

cd /data/eyra/recordings
ls -1 session_* | (expr $(wc -l) / 2 - $(ls . | wc -l))
