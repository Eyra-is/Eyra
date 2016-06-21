#!/bin/bash
# Copyright 2016 Matthias Petursson
# Apache 2.0

display_usage() { 
    echo -e "
Usage: $0 tokenDump numberedTokens
Parses a tokenDump (dump of tokens from mysql database, i.e. a couple of lines with 'INSERT INTO...' only)\
and turns it into a file with format 'tokId token' (same format genGraphs.sh and *GenGraphs.py need).
Just a bunch of sed commands mostly.
" 
} 
if [[ ( $1 == "--help") ||  $1 == "-h" ]] 
then 
    display_usage
    exit 0
fi 
if [[ "$#" -ne 2 ]]; then
    display_usage
    exit 1
fi

cat $1 | sed "s/INSERT INTO \`token\` VALUES //g" | sed "s/([0-9]*,'//g" | sed "s/',[0-1],'[jv|en]*')//g" | sed "s/;$//g" | sed "s/\\\'/'/g" | tr "," "\n" | nl -n ln | sed "s/ \+/ /g" | sed "s/\t\+//g" > $2