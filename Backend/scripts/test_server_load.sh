#!/bin/bash
#
# Copyright 2016 The Eyra Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File author/s:
#     Matthias Petursson <oldschool01123@gmail.com>

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