#!/bin/bash

cd ../server-interface/recordings
for ses in $(ls -1)
do
    echo "$ses: "$(ls -1 $ses | (expr $(wc -l) / 2))
done