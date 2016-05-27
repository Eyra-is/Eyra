#!/bin/bash
# Copyright 2016 Matthias Petursson
# Apache 2.0

# Get the script directory
SDIR=$( dirname $( readlink -f $0 ) )
cd "$SDIR"

cd /data/eyra/recordings
for ses in $(ls -1)
do
    echo "$ses: "$(ls -1 $ses | (expr $(wc -l) / 2))
done