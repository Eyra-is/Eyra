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

import MySQLdb
import os
import sys
import csv
import sh
import uuid

# mv out of script directory and do relative imports from server-interface.
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir, 'server-interface'))
sys.path.append(newPath)
from config import dbConst # to connect to database
from util import log
sys.path.remove(newPath)
del newPath

EYRA_ROOT = '/data/eyra/recordings'
_db = MySQLdb.connect(**dbConst)

def run(data_path, tsv_name):
    """
    Converts data from one format to Eyra, writes to MySQL database and copies files to filesystem.

    Expects data in <data_path> on format as described in script description.
    """
    with open(os.path.join(data_path, tsv_name), 'r') as f:
        tsv_data = list(csv.reader(f, delimiter='\t'))

    for i in os.listdir(data_path):
        if os.path.isdir(os.path.join(data_path, i)):
            session_id = insertIntoDatabase(i, tsv_data)
            copyToFilesystem(data_path, i, session_id)

    # finally commit if no exceptions
    _db.commit()

def insertIntoDatabase(session_path, tsv_data):
    """
    Converts all possible metadata to Eyra format (see e.g. Backend/db/schema_setup.sql)

    tsv_data with metadata 
        "eyra_id unique_id transcript speaker place_condition speaker_gender
         device device_serial_number device_IMEI device_android_id prologue_length 
         epilogue_length total_audio_samples audio_sample_size sample_coding cluster_id 
         sample_rate atomic_type atomic_size audio_sample_type"

    if a prompt in tsv_data is not in the database, it is added, with valid=0 and prompLabel='ex'

    returns newly created session_id

    """

    session_name = os.path.basename(session_path)
    log("Processing session: {}".format(session_name))

    placeholder = 'N/A'
    session_id = None
    start_time = str(uuid.uuid4()) # uuid just to bypass unique constraints

    i = 0
    for row in tsv_data:
        if i == 0:
            # skip header
            i += 1
            continue
        if row[15] == session_name:
            filename = row[0]
            prompt = row[2]
            speaker = row[3]
            environment = row[4]
            gender = row[5]
            device = row[6]
            device_android_id = row[9] # use the android id since that's what the app uses currently

            try:
                cur = _db.cursor()

                # device
                cur.execute('SELECT id FROM device WHERE userAgent=%s AND imei=%s',
                            (device, device_android_id))
                device_id = cur.fetchone()
                if not device_id:
                    # if we haven't already inserted device, do it now
                    cur.execute('INSERT INTO device (userAgent, imei) VALUES (%s, %s)',
                                (device, device_android_id))
                    device_id = cur.lastrowid
                else:
                    device_id = device_id[0]
                # speaker
                cur.execute('SELECT id FROM speaker WHERE name=%s AND deviceImei=%s',
                            (speaker, device_android_id))
                speaker_id = cur.fetchone()
                if not speaker_id:
                    cur.execute('INSERT INTO speaker (name, deviceImei) VALUES (%s, %s)',
                                (speaker, device_android_id))
                    speaker_id = cur.lastrowid
                    # speaker_info
                    cur.execute('INSERT INTO speaker_info (speakerId, s_key, s_value) VALUES (%s, %s, %s)',
                                (speaker_id, "gender", gender))
                else:
                    speaker_id = speaker_id[0]
                # token
                cur.execute('SELECT id FROM token WHERE inputToken=%s',
                            (prompt,))
                token_id = cur.fetchone()
                if not token_id:
                    # token must not be in database, simply add it
                    cur.execute('INSERT INTO token (inputToken, valid, promptLabel) VALUES (%s, %s, %s)',
                                (prompt, str(0), 'ex'))
                    token_id = cur.lastrowid
                else:
                    token_id = token_id[0]
                # session
                cur.execute('SELECT id FROM session WHERE speakerId=%s AND instructorId=%s \
                             AND deviceId=%s AND location=%s AND start=%s AND end=%s and comments=%s',
                            (speaker_id, 1, device_id, 'custom location', start_time, placeholder, environment))
                session_id = cur.fetchone()
                if not session_id:
                    cur.execute('INSERT INTO session (speakerId, instructorId, deviceId, location, start, end, comments) \
                                 VALUES (%s, %s, %s, %s, %s, %s, %s)',
                                (speaker_id, 1, device_id, 'custom location', start_time, placeholder, environment))
                    session_id = cur.lastrowid
                else:
                    session_id = session_id[0]
                # recording
                cur.execute('INSERT INTO recording (tokenId, speakerId, sessionId, filename) \
                             VALUES (%s, %s, %s, %s)',
                            (token_id, speaker_id, session_id, filename))
            except MySQLdb.Error as e:
                msg = 'Error inserting info into database.'
                log(msg, e)
                raise
        i += 1

    if session_id is not None:
        return session_id
    else:
        raise ValueError('Warning, no data found for current session, could be a session folder not in .tsv, \
            aborting (remember that files are still copied to EYRA_ROOT even though the db is untouched.')

def copyToFilesystem(data_path, session_path, session_id):
    """
    copies:
        data_path/session_path
            wav1.wav
            wav1.txt
            wav2.wav
            wav2.txt
            ..
    to:
        /data/eyra/recordings/session_<session_id>/wav*.{wav,txt}
    """
    recPath = os.path.join(EYRA_ROOT, 'session_{}'.format(session_id))
    os.makedirs(recPath, exist_ok=True)
    full_session_path = os.path.join(data_path, session_path)

    log('Copying all files from {} to {}'.format(full_session_path, recPath))
    
    sh.cp(sh.glob(full_session_path + '/*'), recPath)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Transfers data on a different format from Eyra to Eyra format. Writes to MySQL database and
        places on the filesystem.

        Parses data on the following format:
            - session based folders with unique ids as foldernames. 
            - .tsv file with metadata 
                "eyra_id unique_id transcript speaker place_condition speaker_gender
                 device device_serial_number device_IMEI device_android_id prologue_length 
                 epilogue_length total_audio_samples audio_sample_size sample_coding cluster_id 
                 sample_rate atomic_type atomic_size audio_sample_type"
              where eyra_id is the filename.
            - and filename.wav and filename.txt (with the prompt) for each session.

        E.g. data_path
                some_id1
                    wav1.wav
                    wav1.txt
                    ..
                some_id2
                    wav10.wav
                    wav10.txt
                    ..
                ..
                data.tsv""")
    parser.add_argument('data_path', type=str, help='Path to the data on format as in description.')
    parser.add_argument('tsv_name', type=str, help='Basename of the .tsv file located in <data_path>.')
    args = parser.parse_args()

    run(args.data_path, args.tsv_name)