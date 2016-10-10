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

# Parses our Eyra database and outputs relevant info in a single .tsv file.

import os
import MySQLdb
import sys

# mv out of scripts directory and do relative imports from there.
newPath = os.path.abspath(os.path.join( os.path.dirname(__file__), 
                                        os.path.pardir, 
                                        'server-interface'))
sys.path.append(newPath)
from config import dbConst
sys.path.remove(newPath)
del newPath

dbConst['user'] = 'root'
_db = MySQLdb.connect(**dbConst) # modify ../server-interface/config.py if you want to connect to different database
verbose = False

def run(rec_path, out_tsv):
    cur = _db.cursor()

    cur.execute('SELECT recording.id, inputToken, filename, session.id '
                'FROM recording, token, session '
                'WHERE recording.sessionId = session.id '
                'AND recording.tokenId = token.id')

    metadata = cur.fetchall()

    print('metadata:', metadata[20:40])

    # have to get speakers separately, because of the key/value system
    genders, yobs, heights = None, None, None
    for key in ('gender', 'dob', 'height'):
        query = 'SELECT recording.id, speaker.name, speaker_info.s_value '\
                'FROM recording, speaker, speaker_info '\
                'WHERE recording.speakerId = speaker.id '\
                'AND speaker.id = speaker_info.speakerId '\
                'AND recording.speakerId = speaker_info.speakerId '\
                'AND speaker_info.s_key = %s'

        if key == 'gender':
            # fix for the rename of the original key which was 'sex'
            cur.execute('{} OR speaker_info.s_key = %s)'.format(query.replace('AND speaker_info', 'AND (speaker_info')),
                        (key, 'sex'))
        else:
            cur.execute(query, (key,))

        if key == 'gender':
            genders = cur.fetchall()
        elif key == 'dob':
            yobs = cur.fetchall()
        elif key == 'height':
            heights = cur.fetchall()
        else:
            raise ValueError('Some confusion with key names?')

    print(len(genders), len(yobs), len(heights))

    with open(out_tsv, 'w') as f:
        f.write('File\tSpeaker\tAge\tGender\tHeight [cm]\tText\n')

        for rec in metadata:
            recId = rec[0]
            prompt = rec[1]
            filename = rec[2]
            if verbose:
                print('Processing file: {}'.format(filename))
            sessionId = rec[3]
            try:
                speaker = next(genderInfo[1] for genderInfo in genders if genderInfo[0] == recId)
            except StopIteration as e:
                speaker = ''
            try:
                # the year 2016 - year of birth = age
                age = 2016 - int(next(yobInfo[2] for yobInfo in yobs if yobInfo[0] == recId))
            except (StopIteration, ValueError) as e:
                age = ''
            try:
                gender = next(genderInfo[2] for genderInfo in genders if genderInfo[0] == recId)
            except StopIteration as e:
                gender = ''
            try:
                height = next(heightInfo[2] for heightInfo in heights if heightInfo[0] == recId)
            except StopIteration as e:
                height = ''
            f.write('{file}\t{speaker}\t{age}\t{gender}\t{height}\t{text}\n'.format(
                sesId=sessionId,
                file=filename,
                speaker=speaker,
                age=age,
                gender=gender,
                height=height.replace(' cm ',''),
                text=prompt
            ))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Parses Eyra database (database) and outputs relevant info as a single .tsv file (outtsv).
        eyradir is the eyra_root, i.e. the dir containing the session_X folders with the wavs.""")
    parser.add_argument('rec_path', type=str, help='Path to the recordings, should be the parent folder of all the session_X folders. E.g. /data/eyra/recordings.')
    parser.add_argument('out_tsv', type=str, help='Path to where you want the .tsv file saved.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Increase verrbosity.')
    args = parser.parse_args()

    if args.verbose:
        verbose = True

    run(args.rec_path, args.out_tsv)