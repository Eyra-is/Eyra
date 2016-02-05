#!/bin/bash

# Get the script directory
SDIR=$( dirname $( readlink -f $0 ) )
cd "$SDIR"

RECORDINGSPATH="../server-interface"
RECORDINGSROOT="/recordings"
BACKUPPATH="../backup"
BACKUPROOT="/$(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [ ! -d "$BACKUPPATH" ]; then
	mkdir "$BACKUPPATH"
fi

mkdir "$BACKUPPATH$BACKUPROOT"

# back up mysql database
mysqldump recordings_master -u root > "$BACKUPPATH$BACKUPROOT"/backup.sql

# back up the recordings and other files
cp -r "$RECORDINGSPATH$RECORDINGSROOT" "$BACKUPPATH$BACKUPROOT" 
