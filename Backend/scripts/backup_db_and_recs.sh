#!/bin/bash
# Copyright 2016 Matthias Petursson
# Apache 2.0

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
