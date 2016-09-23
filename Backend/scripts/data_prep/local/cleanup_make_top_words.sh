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

# Make a list of top 100 words using prompts on same format as needed to make decoding graphs.

display_usage() { 
    echo "Usage:
$0 prompts
Prompts should be a file with format: 'id prompt' where prompt is e.g. 'the quick brown fox' \
and a space separating the id and the prompt."
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

prompts=$1

# thanks for the tolowercase line in sed, Stéphane Chazelas, http://unix.stackexchange.com/a/228570/146563
mkdir -p local/cleanup; tar -xzf local/cleanup.tgz -C local/cleanup
utils/sym2int.pl --map-oov "<UNK>" local/cleanup/words.syms <(cut -d' ' -f 2- "$prompts" \
  | sed 's/[[:upper:]]/\l&/g') \
  | awk 'BEGIN{total=0;}{a[$1]++; total++;}END{for(k in a)printf "%f %d\n", a[k]/total,k}' RS=" |\n" \
  | sort -n -r \
  | head -101 \
  | tail -n 100 > local/cleanup/top_words.int
