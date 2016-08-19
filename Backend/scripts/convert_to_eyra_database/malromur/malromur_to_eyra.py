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

# Transfers data from Icelandic speech corpus Malromur (http://www.malfong.is/index.php?lang=en&pg=malromur)
# to Eyra format. Note that this was used on the full Malromur which currently is not online. [2016/07/12]

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
oldLog = None

def disableLogFunction():
    """
    Disable normal logging, keep exception logging.
    """
    global log
    oldLog = log
    def unverboseLog(a,b=None):
        if b:
            oldLog(a,b)
        else:
            pass
    log = unverboseLog

def run(data_path, csv_path, prompt_path):
    """
    Converts data from one format to Eyra, writes to MySQL database and copies files to filesystem.

    Expects data in <data_path> on format as described in script description.
    """
    with open(csv_path, 'r') as f:
        csv_data = list(csv.reader(f, delimiter=','))
    with open(prompt_path, 'r') as f:
        prompts = [ x[1] for x in list(csv.reader(f, delimiter='\t')) ]

    insertPromptsIntoDatabase(prompts)
    j = 1
    for rec in os.listdir(data_path):
        if rec.endswith('.wav'):
            print("Processing rec ({}): {}".format(j, rec))
            session_id, prompt = insertIntoDatabase(rec, csv_data)
            copyToFilesystem(data_path, rec, session_id, prompt)
            j += 1

    # finally commit if no exceptions
    _db.commit()

def insertPromptsIntoDatabase(prompts: list) -> None:
    try:
        cur = _db.cursor()

        # idea from Raymond Hettinger, from answer here: http://stackoverflow.com/a/8316210/5272567
        var_string = ','.join('T' * len(prompts)) # T is a placeholder
        var_string = var_string.replace('T', '(%s,1,\'is\')')
        query_string = 'INSERT INTO token (inputToken, valid, promptLabel) '+\
                       'VALUES {};'.format(var_string)
        cur.execute(query_string, prompts)
    except MySQLdb.Error as e:
        msg = 'Error inserting prompts into database.'
        log(msg, e)
        raise

def insertIntoDatabase(rec_name, csv_data) -> (int, str):
    """
    Converts all possible metadata to Eyra format (see e.g. Backend/db/schema_setup.sql)

    csv_data with metadata 
        filename,
        filetype,
        language,
        environment,
        date/time,
        unused_info,
        unused_info,
        prompt,
        username=<usr>;unused_info;device=<imei>;session_id=<id>;gender=<gender>;age=<age_interval>;latitude=<latitude>;longitude=<longitude>,
        unused_info

    if a prompt in csv_data is not in the database, it is added, with valid=0 and prompLabel='ex'

    if device and username are the same, interprets as the same session. 

    returns newly created session_id and the prompt extracted from metadata
    """

    rec_name = os.path.basename(rec_name)

    placeholder = 'N/A'
    session_id = None
    start_time = str(uuid.uuid4()) # uuid just to bypass unique constraints

    for row in csv_data:
        if row[0] == rec_name:
            filename = row[0]
            environment = row[3]
            prompt = row[7]
            speaker = row[8].split(';')[0].replace('username=','')
            device_imei = row[8].split(';')[2].replace('device=','')
            gender = row[8].split(';')[4].replace('gender=','')
            age = row[8].split(';')[5].replace('age=','')
            location = 'lat:{},lon:{}'.format(row[8].split(';')[6].replace('latitude=',''),
                                              row[8].split(';')[7].replace('longitude=',''))

            try:
                cur = _db.cursor()

                # device
                cur.execute('SELECT id FROM device WHERE imei=%s',
                            (device_imei,))
                try:
                    device_id = cur.fetchone()[0]
                except TypeError as e:
                    # if we haven't already inserted device, do it now
                    cur.execute('INSERT INTO device (userAgent, imei) VALUES (%s, %s)',
                                (placeholder, device_imei))
                    device_id = cur.lastrowid
                # speaker
                cur.execute('SELECT id FROM speaker WHERE name=%s AND deviceImei=%s',
                            (speaker, device_imei))
                try:
                    speaker_id = cur.fetchone()[0]
                except TypeError as e:
                    cur.execute('INSERT INTO speaker (name, deviceImei) VALUES (%s, %s)',
                                (speaker, device_imei))
                    speaker_id = cur.lastrowid
                    # speaker_info
                    cur.execute('INSERT INTO speaker_info (speakerId, s_key, s_value) VALUES (%s, %s, %s)',
                                (speaker_id, "gender", gender))
                    cur.execute('INSERT INTO speaker_info (speakerId, s_key, s_value) VALUES (%s, %s, %s)',
                                (speaker_id, "age", age))
                # token
                cur.execute('SELECT id FROM token WHERE inputToken=%s',
                            (prompt,))
                try:
                    token_id = cur.fetchone()[0]
                except TypeError as e:
                    # token must not be in database, simply add it
                    cur.execute('INSERT INTO token (inputToken, valid, promptLabel) VALUES (%s, %s, %s)',
                                (prompt, str(0), 'ex'))
                    token_id = cur.lastrowid
                # session, interpret it as the same session if speaker and device are same
                cur.execute('SELECT id FROM session WHERE speakerId=%s AND deviceId=%s',
                            (speaker_id, device_id))
                try:
                    session_id = cur.fetchone()[0]
                except TypeError as e:
                    cur.execute('INSERT INTO session (speakerId, instructorId, deviceId, location, start, end, comments) \
                                 VALUES (%s, %s, %s, %s, %s, %s, %s)',
                                (speaker_id, 1, device_id, location, start_time, placeholder, environment))
                    session_id = cur.lastrowid
                # recording
                cur.execute('INSERT INTO recording (tokenId, speakerId, sessionId, filename) \
                             VALUES (%s, %s, %s, %s)',
                            (token_id, speaker_id, session_id, filename))
            except MySQLdb.Error as e:
                msg = 'Error inserting info into database.'
                log(msg, e)
                raise

    if session_id is not None:
        if prompt is not None:
            return session_id, prompt
        else:
            raise ValueError('Warning, couldn\'t find a prompt.')
    else:
        raise ValueError('Warning, no data found for current recording, could be a rec not in .csv, \
            aborting (remember that files are still copied to EYRA_ROOT even though the db is untouched.')

def copyToFilesystem(data_path, rec_name, session_id, prompt):
    """
    copies:
        data_path/rec_name
    to:
        /data/eyra/recordings/session_<session_id>/wav*.{wav,txt}

    where *.txt contains the corresponding prompt.
    """
    recPath = os.path.join(EYRA_ROOT, 'session_{}'.format(session_id))
    os.makedirs(recPath, exist_ok=True)
    full_rec_name = os.path.join(data_path, rec_name)

    log('Copying file from {} to {}'.format(full_rec_name, recPath))
    sh.cp(full_rec_name, recPath)

    promptPath = os.path.join(recPath, rec_name[:-4]+'.txt')
    log('Writing prompt to file: {}'.format(promptPath))
    with open(promptPath, 'w') as f:
        f.write(prompt)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Transfers data from Icelandic speech corpus Malromur (http://www.malfong.is/index.php?lang=en&pg=malromur) 
        to Eyra format. Writes to MySQL database and copies to the filesystem. This was used on the full 
        Malromur set though, not the one currently online [2016/07/12].

        Parses data on the following format:
            - a folder containing the entire audio with no sub-folders (<data_path>)
            - .csv file with metadata 
                filename,
                filetype,
                language,
                environment,
                date/time,
                unused_info,
                unused_info,
                prompt,
                username=<usr>;gaiaid=<instructor>;device=<imei>;session_id=<id>;gender=<gender>;age=<age_interval>;latitude=<latitude>;longitude=<longitude>,
                unused_info
            - a prompt file on the format 'id[TAB]prompt', e.g.
                prompt_1    The quick brown unoriginal fox
                prompt_2    Jumped
                ...
        """)
    parser.add_argument('data_path', type=str, help='Path to the data folder.')
    parser.add_argument('csv_path', type=str, help='Path to the .csv file.')
    parser.add_argument('prompt_path', type=str, help='Path to the prompt file, format: \'promptId[TAB]prompt\', one on each line.')
    parser.add_argument('--verbose','-v', action='store_true', help='Get a more verbose output.')
    args = parser.parse_args()

    if not args.verbose:
        disableLogFunction()

    run(args.data_path, args.csv_path, args.prompt_path)