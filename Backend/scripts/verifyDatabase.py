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

# Verifies that the sql database matches the files/info on the system.

import os
import MySQLdb
import sys

# mv out of scripts directory and do relative imports from there.
newPath = os.path.abspath(os.path.join( os.path.dirname(__file__), 
                                        os.path.pardir, 
                                        'server-interface'))
sys.path.append(newPath)
from config import dbConst
from util import isWavHeaderOnly
sys.path.remove(newPath)
del newPath

dbConst['user'] = 'root'
_db = MySQLdb.connect(**dbConst) # modify ../server-interface/config.py if you want to connect to different database
errors = 0
warnings = 0
verbosity = 0

def error(arg):
    global errors
    errors += 1
    if verbosity >= 1:
        print('Error:', arg)

def warning(arg):
    global warnings
    warnings += 1
    if verbosity >= 2:
        print('Warning:', arg)

def run(rec_path):
    cur = _db.cursor()

    cur.execute('SELECT recording.id, inputToken, filename, session.id '
                'FROM recording, token, session '
                'WHERE recording.sessionId = session.id '
                'AND recording.tokenId = token.id ')

    data = cur.fetchall()

    #print('data:', data[20:40])

    for rec in data:
        prompt = rec[1]
        filename = rec[2]
        sesId = rec[3]
        absFilename = os.path.join(rec_path, 'session_{}'.format(sesId), filename)
        if not os.path.exists(absFilename):
            error('File doesn\'t exist, {}'.format(absFilename))
            continue
        if isWavHeaderOnly(absFilename):
            warning('File only contains wav header, {}'.format(absFilename))

        with open('{}.txt'.format('.'.join(absFilename.split('.')[:-1])), 'r') as f:
            line = f.readline()
            line = line[:-1] if '\n' in line else line
            if line != prompt:
                error('Prompt in backup file doesn\'t match prompt from database, {}'.format(absFilename))

    print('Finished with {} errors and {} warnings out of {} recordings checked.'.format(errors, warnings, len(data)))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Verifies that rec paths in database correspond to files, and that prompts in text files
        match prompts in database.""")
    parser.add_argument('rec_path', type=str, help='Path to the recordings, should be the parent folder of all the session_X folders. E.g. /data/eyra/recordings.')
    parser.add_argument('verbosity', type=int, nargs='?', help='0: only print error/warning count. 1: only print errors and error/warning count. 2: print everything.')
    args = parser.parse_args()

    if args.verbosity:
        verbosity = args.verbosity

    run(args.rec_path)