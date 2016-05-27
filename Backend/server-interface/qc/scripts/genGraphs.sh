#!/bin/bash
# Copyright 2016 Matthias Petursson
# Apache 2.0

display_usage() { 
    echo -e "Usage:\n$0 module token_file graphs_scp_file [--concurrency,-c CONCURRENCY=1]\
             \n\nCreates decoding graphs for Marosijo and Cleanup module. Using CONCURRENCY threads.\n\
             module is 'marosijo' for marosijo and 'cleanup' for cleanup
             token_file is a path to a file with format 'tokId token' where tokId is the same id as in MySQL database for the token.\n\
             graphs_scp_file is a path to where the resulting .scp/.ark files are stored.\n" 
} 
if [[ ( $1 == "--help") ||  $1 == "-h" ]] 
then 
    display_usage
    exit 0
fi 
if [[ "$#" -lt 3 || "$#" -gt 5 ]]; then
    display_usage
    exit 1
fi

# Get the script directory
SDIR=$( dirname $( readlink -f $0 ) )
cd "$SDIR"

if [[ $1 == "marosijo" ]]; then
    module="Marosijo"
else 
    if [[ $1 == "cleanup" ]]; then
        module="Cleanup"
    else
        display_usage
        exit 1
    fi
fi
token_file=$2
graphs_scp_file=$3
conc=1
if [[ ( $5 )]]; then
    conc=$5
fi
destDir=$(dirname "${graphs_scp_file}")

split -n l/$conc $token_file "graph_gen_"

for f in graph_gen_*; do
    python3 $module"GenGraphs.py" $f $destDir"/"$f".ark" $f".scp" &
done
wait

cat graph_gen_*.scp | sort -k 1 -n > $graphs_scp_file
rm graph_gen_*

