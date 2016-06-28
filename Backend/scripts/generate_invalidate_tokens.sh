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