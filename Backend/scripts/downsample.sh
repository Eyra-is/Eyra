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

# Downsamples Eyra data and copies it to new location.

display_usage() { 
    echo -e "
Usage: $0 [-c] eyra_root destination sample_rate
Downsamples all Eyra data in eyra_root and copies it to destination (with new sample_rate).\
 eyra_root contains the session_* folders. E.g. /data/eyra/recordings\
 Converts to .flac if -c flag is provided.
" 
} 
if [[ ( $1 == "--help") ||  $1 == "-h" ]]; then 
    display_usage
    exit 0
fi 
if [[ "$#" -ne 3 && "$#" -ne 4 ]]; then
    display_usage
    exit 1
fi

# thanks, http://wiki.bash-hackers.org/howto/getopts_tutorial
flac=0
while getopts ":c" opt; do
  case $opt in
    c)
        echo "Will convert to .flac" >&2
        flac=1
        eyra_root=$2
        dest=$3
        sr=$4
        ;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
  esac
done
if [[ $flac -eq 0 ]]; then
    eyra_root=$1
    dest=$2
    sr=$3
fi

downsampleAndCopyFolder() {
    folder=$1
    folder_name=$(basename "$folder")
    if [[ "$2" == "lost" ]]; then
        folder_name="lost"/"$folder_name"
    fi
    echo "Processing folder: $folder"

    mkdir -p "$dest"/"$folder_name"
    for i in "$folder"/*.wav; do
        wav_name=$(basename "$i")
        sox "$i" -r 16000 -t wav "$dest"/"$folder_name"/"$wav_name"
        if [[ $flac -eq 1 ]]; then
            flac -s -f --delete-input-file --keep-foreign-metadata --compression-level-3 "$dest"/"$folder_name"/"$wav_name"
        fi
    done    
    cp "$folder"/*.txt "$dest"/"$folder_name"
}

for session in "$eyra_root"/*; do
    session_name=$(basename "$session")
    if [ -d "$session" ]; then
        if [[ "$session_name" == 'lost' ]]; then
            for i in "$session"/*; do
                downsampleAndCopyFolder "$i" "lost"
            done
        else
            downsampleAndCopyFolder "$session"
        fi
    fi
done
