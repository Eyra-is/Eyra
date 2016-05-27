#!/bin/bash
# Copyright 2016 Matthias Petursson
# Apache 2.0

display_usage() { 
    echo -e "Usage:\n$0 invalid_ids\n\n\
Generate the invalidate_tokens.sql file, which marks all tokens with ids\
from invalid_ids file (1 on each line) as invalid in mysql database when\
erase_and_rewind is run." 
} 
if [[ ( $1 == "--help") ||  $1 == "-h" ]] 
then 
    display_usage
    exit 0
fi 
if [ "$#" -ne 1 ]; then
    display_usage
    exit 1
fi

# Get the script directory
SDIR=$( dirname $( readlink -f $0 ) )
cd "$SDIR"

awk -v nlines="$(wc -l < $1)" ' BEGIN { printf "update token\n\
set valid=FALSE\n\
where id in\n\
("; }\
\
{ printf $0; if(NR<nlines) print ","; }\
\
END { print ");" } ' $1 > ../db/invalidate_tokens.sql