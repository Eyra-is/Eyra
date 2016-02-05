#!/bin/bash

# Get the script directory
SDIR=$( dirname $( readlink -f $0 ) )
cd "$SDIR"

cd ../server-interface/recordings
for ses in $(ls -1)
do
    echo "$ses: "$(ls -1 $ses | (expr $(wc -l) / 2))
done