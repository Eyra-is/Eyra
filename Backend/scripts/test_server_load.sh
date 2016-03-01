#!/bin/bash

# https://www.petefreitag.com/item/689.cfm
# thank you Pete Freitag

display_usage() { 
    echo -e "Usage:\n$0 numRequests maxConcRequests\n\nTest server with numRequests requests and a maximum of maxConcRequests running concurrently. Example: ./test_server_load.sh 10000 1000" 
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

ab -n $1 -c $2 https://localhost/