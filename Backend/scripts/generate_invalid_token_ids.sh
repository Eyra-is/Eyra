#!/bin/bash
# Copyright 2016 Matthias Petursson
# Apache 2.0

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

total_tokens=$1
good_tokens=$2
join -v1 -t $'\t' -1 2 -2 1 <(sort -k2 -t $'\t' $total_tokens) <(sort $good_tokens) \
  | cut -f2 | sort -n
