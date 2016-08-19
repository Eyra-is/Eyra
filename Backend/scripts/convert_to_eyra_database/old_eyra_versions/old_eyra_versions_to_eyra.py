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

# Transfers data from certain older versions of Eyra to the current one. [2016-08-18]
# Just here for reference. Someone might find it useful to combine a couple of Eyra databases.

import MySQLdb
import os
import sys
import re
import sh

# similar to what's in config
dbConst = dict(host='localhost',
    user='root', # no password
    db='CHANGEME', # and other
    use_unicode=True,
    charset='utf8')

EYRA_ROOT = '/data/eyra/recordings'
oldLog = None
dbNames = ['malr_old', 'malr_new', 'new_new', 'mim']
tables = ['token', 'device', 'instructor', 'speaker', 'speaker_info', 'session', 'recording']

dbs = {}
dbConst['db']   = 'Z_malromur_old'
dbs['malr_old'] = MySQLdb.connect(**dbConst)
dbConst['db']   = 'malromur_newer'
dbs['malr_new'] = MySQLdb.connect(**dbConst)
dbConst['db']   = '7Z_newer_newer'
dbs['new_new']  = MySQLdb.connect(**dbConst)
dbConst['db']   = '32Z_mim_tokens'
dbs['mim']      = MySQLdb.connect(**dbConst)
dbConst['db']   = 'recordings_master'
dbs['eyra']     = MySQLdb.connect(**dbConst)

# lets make a dictionary mapping from the old ids (to be unique we need (id, db))
# for all different tables, format:
# idHash
#   malr_old
#     token
#       2 : 51
#       ..
#     device
#       4 : 15
#       ..
#     ..
#   ..
idHash = {}
for n in dbNames:
    idHash[n] = {}
    for t in tables:
        idHash[n][t] = {}

def run(malr_old_path, malr_new_path, new_new_path, mim_path) -> None:
    for db in dbNames:
        print('Inserting SQL for: {}'.format(db))
        insertDevice(db)
        insertInstructor(db)
        insertToken(db)
        if db == 'malr_old':
            insertSpeakerMalrOld()
        else:
            insertSpeaker(db)
        insertSession(db)
        insertRecording(db)

        print('Copying files for: {}'.format(db))
        copySessionsToFilesystem(db, locals()['{}_path'.format(db)])

    dbs['eyra'].commit()


def insertDevice(db) -> None:
    """
    Transfers all data from table device from db to table device in eyra db.
    """
    skipFirstRow = True

    cur = dbs[db].cursor()
    eyraCur = dbs['eyra'].cursor()
    cur.execute('SELECT * FROM device')
    rows = cur.fetchall()
    for row in rows:
        if skipFirstRow:
            skipFirstRow = False
            continue
        eyraCur.execute('INSERT INTO device (userAgent, imei) VALUES ({})'.format(
                ','.join(['%s']*len(row[1:]))
            ),
            row[1:]
        )
        idHash[db]['device'][row[0]] = eyraCur.lastrowid

def insertInstructor(db) -> None:
    skipFirstRow = True

    cur = dbs[db].cursor()
    eyraCur = dbs['eyra'].cursor()
    cur.execute('SELECT * FROM instructor')
    rows = cur.fetchall()
    for row in rows:
        if skipFirstRow:
            skipFirstRow = False
            continue

        eyraCur.execute('SELECT id FROM instructor WHERE name=%s AND email=%s',
            (row[1], row[2])
        )
        try:
            instructorId = eyraCur.fetchone()[0]
            print('Instructor: {}, {} already in database.'.format(row[1], row[2]))
            idHash[db]['instructor'][row[0]] = instructorId
        except TypeError as e:
            # no instructor with this name/email already in Eyra database
            eyraCur.execute('INSERT INTO instructor (name, email, phone, address) VALUES ({})'.format(
                    ','.join(['%s']*len(row[1:]))
                ),
                row[1:]
            )
            idHash[db]['instructor'][row[0]] = eyraCur.lastrowid

def insertToken(db) -> None:
    if db == 'malr_old':
        promptLabel = 'mo'
    elif db == 'malr_new':
        promptLabel = 'mn'
    elif db == 'new_new':
        promptLabel = 'nn'
    elif db == 'mim':
        promptLabel = 'mm'
    else:
        raise ValueError('Unknown db? {}'.format(db))

    cur = dbs[db].cursor()
    eyraCur = dbs['eyra'].cursor()
    cur.execute('SELECT * FROM token')
    rows = cur.fetchall()
    for row in rows:
        eyraCur.execute('INSERT INTO token (inputToken, promptLabel) VALUES (%s,%s)',
            (row[1], promptLabel)
        )
        idHash[db]['token'][row[0]] = eyraCur.lastrowid

def insertSpeaker(db) -> None:
    skipFirstRow = True

    cur = dbs[db].cursor()
    eyraCur = dbs['eyra'].cursor()
    cur.execute('SELECT * FROM speaker')
    rows = cur.fetchall()
    for row in rows:
        if skipFirstRow:
            skipFirstRow = False
            continue
        eyraCur.execute('INSERT INTO speaker (name, deviceImei) VALUES ({})'.format(
                ','.join(['%s']*len(row[1:]))
            ),
            row[1:]
        )
        idHash[db]['speaker'][row[0]] = eyraCur.lastrowid

    # and now the speaker info
    cur.execute('SELECT * FROM speaker_info')
    rows = cur.fetchall()
    for row in rows:
        if row[1] == 1:
            continue # in case it's the placeholder speaker
            
        eyraCur.execute('INSERT INTO speaker_info (speakerId, s_key, s_value) VALUES ({})'.format(
                ','.join(['%s']*3)
            ),
            (idHash[db]['speaker'][row[1]], row[2], row[3]) # swap the old speakerId with the new one
        )
        idHash[db]['speaker_info'][row[0]] = eyraCur.lastrowid

def insertSpeakerMalrOld() -> None:
    """
    Special case for malr_old since it didn't have speaker_info, and had the info
    directly in the speaker table.

    Had schema:
    CREATE TABLE `speaker` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `name` varchar(255) NOT NULL,
      `gender` varchar(25) NOT NULL,
      `height` varchar(25) NOT NULL,
      `dob` varchar(25) NOT NULL,
      `deviceImei` varchar(255) NOT NULL DEFAULT '',
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
    """
    skipFirstRow = True

    db = 'malr_old'
    cur = dbs[db].cursor()
    eyraCur = dbs['eyra'].cursor()
    cur.execute('SELECT * FROM speaker')
    rows = cur.fetchall()
    for row in rows:
        if skipFirstRow:
            skipFirstRow = False
            continue
        eyraCur.execute('INSERT INTO speaker (name, deviceImei) VALUES (%s,%s)',
            (row[1], row[5])
        )
        idHash[db]['speaker'][row[0]] = eyraCur.lastrowid

        # and now insert gender, height, dob into speaker_info
        speakerId = idHash[db]['speaker'][row[0]]
        eyraCur.execute('INSERT INTO speaker_info (speakerId, s_key, s_value) VALUES (%s,%s,%s)',
            (speakerId, 'gender', row[2])
        )
        eyraCur.execute('INSERT INTO speaker_info (speakerId, s_key, s_value) VALUES (%s,%s,%s)',
            (speakerId, 'height', row[3])
        )
        eyraCur.execute('INSERT INTO speaker_info (speakerId, s_key, s_value) VALUES (%s,%s,%s)',
            (speakerId, 'dob', row[4])
        )

def insertSession(db) -> None:
    skipFirstRow = True

    cur = dbs[db].cursor()
    eyraCur = dbs['eyra'].cursor()
    cur.execute('SELECT * FROM session')
    rows = cur.fetchall()
    for row in rows:
        if skipFirstRow:
            skipFirstRow = False
            continue
        # handle placeholders
        if row[1] == 1:
            speakerId = 1
        else:
            speakerId = idHash[db]['speaker'][row[1]]
        if row[2] == 1:
            instructorId = 1
        else:
            instructorId = idHash[db]['instructor'][row[2]]
        if row[3] == 1:
            deviceId = 1
        else:
            deviceId = idHash[db]['device'][row[3]]

        eyraCur.execute('INSERT INTO session (speakerId, instructorId, deviceId, '+
                        'location, start, end, comments) VALUES ({})'.format(
                ','.join(['%s']*7)
            ),
            (speakerId, instructorId, deviceId, row[4], row[5], row[6], row[7])
        )
        idHash[db]['session'][row[0]] = eyraCur.lastrowid

def insertRecording(db) -> None:
    cur = dbs[db].cursor()
    eyraCur = dbs['eyra'].cursor()
    cur.execute('SELECT * FROM recording')
    rows = cur.fetchall()
    for row in rows:
        # handle placeholders
        if row[2] == 1:
            speakerId = 1
        else:
            speakerId = idHash[db]['speaker'][row[2]]
        if row[3] == 1:
            sessionId = 1
        else:
            sessionId = idHash[db]['session'][row[3]]
        # all the recordings had the old 'rel_path' parameter, meaning it had
        # more than the filename and an actual path (e.g. recordings/session_7/bla.wav)
        # remove that and leave only bla.wav
        m = re.match('.*session_\d+/(.*)$', row[4])
        filename = m.group(1)
        if '.wav' not in filename:
            raise ValueError('Error, did this rec not contain the old path? {}'.format(row[4]))

        eyraCur.execute('INSERT INTO recording (tokenId, speakerId, sessionId, '+
                        'filename, rec_method) VALUES ({})'.format(
                ','.join(['%s']*5)
            ),
            (idHash[db]['token'][row[1]], speakerId, sessionId, filename, db)
        )
        idHash[db]['recording'][row[0]] = eyraCur.lastrowid

def copySessionsToFilesystem(db, path) -> None:
    """
    Uses the info in idHash[db]['session'] to locate files in path/session_X
    and copy them to their new location EYRA_ROOT/session_Y
    """
    for session in os.listdir(path):
        oldSessionId = session.split('_')[1]
        newSessionId = idHash[db]['session'][int(oldSessionId)]
        newSessionPath = os.path.join(EYRA_ROOT, 'session_{}'.format(newSessionId))
        sh.cp('-r', os.path.join(path, session), newSessionPath)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Transfers data from 4 different older databases recorded with Eyra and combines
        into a single up to date (currently) Eyra database.

        Assumes the databases have been inserted into mysql. 
        Under:
            | 32Z_mim_tokens     |
            | 7Z_newer_newer     |
            | Z_malromur_old     |
            | malromur_newer     |
        and then we have 
            | recordings_master  |
        which we will insert into.

        Thankfully, the file system part has remained unchanged.

        Now if only we had used UUIDs for all the ids!
        """)
    parser.add_argument('malr_old_path', type=str, help='Path to the folder with recordings split into sessions.')
    parser.add_argument('malr_new_path', type=str, help='Path to the folder with recordings split into sessions.')
    parser.add_argument('new_new_path', type=str, help='Path to the folder with recordings split into sessions.')
    parser.add_argument('mim_path', type=str, help='Path to the folder with recordings split into sessions.')
    args = parser.parse_args()

    run(args.malr_old_path, args.malr_new_path, args.new_new_path, args.mim_path)