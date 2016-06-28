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
    echo -e "Usage:
$0 destdir [identifier]
Backs up recordings by doing an sql dump and tar the recordings (at /data/eyra/recordings) and \
copying that to destdir/identifier_date/{backup.sql,recs.tgz}.
identifier is something to identify this current backup, like 'summer_backup'" 
} 
if [[ ( $1 == "--help") ||  $1 == "-h" ]] 
then 
    display_usage
    exit 0
fi 
if [ "$#" -lt 1 ]; then
    display_usage
    exit 1
fi

RECORDINGSPATH="/data/eyra/recordings"
BACKUPPATH=$1
if [ ! -z "$2" ]; then
	IDENTIFIER=$2
else
	IDENTIFIER="misc"
fi
BACKUPROOT="${IDENTIFIER}_$(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [ ! -d "$BACKUPPATH" ]; then
	mkdir -p "$BACKUPPATH"
fi

mkdir "$BACKUPPATH/$BACKUPROOT"

# back up mysql database
mysqldump recordings_master -u root -p > "$BACKUPPATH/$BACKUPROOT"/backup.sql

# back up the recordings and other files
tar -cvzf "$BACKUPPATH/$BACKUPROOT/recs.tgz" "$RECORDINGSPATH" 
