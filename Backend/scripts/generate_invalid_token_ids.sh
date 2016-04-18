#!/bin/bash

display_usage() { 
    echo -e "Usage:\n$0 total_tokens good_tokens\n\n\
Given a total_tokens list and a list of good_tokens (from that list)\
generate the invalid tokens ids (tokens in total_tokens but not in good_tokens.\n\
total_tokens format: 'tokIdTABtoken'\n\
good_tokens format: 'token'" 
} 
if [[ ( $1 == "--help") ||  $1 == "-h" ]] 
then 
    display_usage
    exit 0
fi 
if [ "$#" -ne 2 ]; then
    display_usage
    exit 1
fi

sort -k2 -t $'\t' $1 > tmp1 && \
sort -t $'\t' $2 > tmp2 && \
join -1 2 -2 1 tmp1 tmp2 -t $'\t' | cut -f 2 | sort -n

rm tmp1 tmp2