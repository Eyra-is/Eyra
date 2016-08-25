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

# Remove selected personal information from database and filesystem (usernames are included
# in filenames).

import os
import MySQLdb
import sys
import random

# mv out of scripts directory and do relative imports from there.
newPath = os.path.abspath(os.path.join( os.path.dirname(__file__), 
                                        os.path.pardir, 
                                        'server-interface'))
sys.path.append(newPath)
from config import dbConst
sys.path.remove(newPath)
del newPath

dbConst['user'] = 'root'
_db = MySQLdb.connect(**dbConst)
verbose = False

def run(rec_path, dest_dir, retain_speakers, remove_imei, remove_location, remove_evaluators):
    if not retain_speakers:
        removeSpeakers(rec_path, dest_dir)
    if remove_imei:
        removeImei(dest_dir)
    if remove_location:
        removeLocation(dest_dir)
    if remove_evaluators:
        removeEvaluators(dest_dir)

    _db.commit()

def removeSpeakers(rec_path, dest_dir):
    print('Removing speakers from database.')
    cur = _db.cursor()
    cur.execute('SELECT id, name FROM speaker')
    speakers = list(cur.fetchall())
    random.shuffle(speakers)
    # idToSpeaker = {
    #   'speakerId' : 'speaker0',
    #   'speakerId' : 'speaker1',
    #   ..
    # }
    idToSpeaker = {}
    for i, s in enumerate(speakers):
        idToSpeaker[s[0]] = 'speaker{}'.format(i)

    # write the oldSpeaker -> newSpeaker file
    print('Creating hash file for speakers.')
    with open(os.path.join(dest_dir, 'speakers.tsv'), 'w') as f:
        f.write('speakerId\toldName\tnewName\n')
        for s in speakers:
            f.write('{}\t{}\t{}\n'.format(s[0], s[1], idToSpeaker[s[0]]))

    # update our speakers by overwriting the previous ones with our new ones
    # thanks Michiel de Mare, http://stackoverflow.com/questions/3432/multiple-updates-in-mysql
    cur.execute('INSERT INTO speaker (id, name) '+
                'VALUES {} ON DUPLICATE KEY UPDATE name = VALUES(name)'
                .format
                    (
                        ','.join([str((x[0], idToSpeaker[x[0]])) for x in speakers])      
                    )
                )

    print('Removing speakers from file names.')
    for session in os.listdir(rec_path):
        for f in os.listdir(os.path.join(rec_path, session)):
            # because speaker names theoretically could have duplicates,
            # we have to use the session number and speaker name
            # for a definitely correct speaker id.
            speakerName = '_'.join(f.split('_')[0:-1]) # just in case someone wrote _ in their name, take everything up until the last _
            cur.execute('SELECT speakerId FROM session WHERE id=%s',
                        (session.split('_')[-1],))
            speakerId = cur.fetchone()[0]
            newSpeaker = idToSpeaker[speakerId]
            # make sure speakerId from session has the same name as our speaker.
            speakerFromDb = speakers[int(newSpeaker[7:])][1]
            if (speakerName != speakerFromDb and speakerName.replace('-', ' ') != speakerFromDb):
                # apparently spaces in db were changed to dashes in the filenames. 
                # This particular code fragment of course could break if someone had 
                # spaces and dashes in his name.
                raise ValueError(  'Error, speaker name from file: {} not equal to speaker name from db: {}'
                                    .format(speakerName, speakerFromDb))
            
            if verbose:
                print(  'Renaming file: {}, changing: {} to {}'
                        .format(os.path.join(rec_path, session, f), speakerName, newSpeaker))
            os.rename(  os.path.join(rec_path, session, f), 
                        os.path.join(rec_path, session, f.replace(speakerName, newSpeaker)))

def removeImei(dest_dir):
    print('Removing imei.')
    cur = _db.cursor()
    cur.execute('SELECT id, imei FROM device')
    devices = list(cur.fetchall())
    # idToImei = {
    #   'deviceId' : 'imei1',
    #   'deviceId' : 'imei2',
    #   ..
    # }
    idToImei = {}
    oldImeiToNewImei = {}
    for i, s in enumerate(devices):
        newImei = 'imei{}'.format(i+1)
        idToImei[s[0]] = newImei
        oldImeiToNewImei[s[1]] = newImei

    # write the oldImei -> newImei file
    print('Creating hash file for imeis.')
    with open(os.path.join(dest_dir, 'imeis.tsv'), 'w') as f:
        f.write('deviceId\toldImei\tnewImei\n')
        for s in devices:
            f.write('{}\t{}\t{}\n'.format(s[0], s[1], idToImei[s[0]]))

    # update our devices by overwriting the previous ones with our new ones
    # thanks Michiel de Mare, http://stackoverflow.com/questions/3432/multiple-updates-in-mysql
    cur.execute('INSERT INTO device (id, imei) '+
                'VALUES {} ON DUPLICATE KEY UPDATE imei = VALUES(imei)'
                .format
                    (
                        ','.join([str((x[0], idToImei[x[0]])) for x in devices])      
                    )
                )

    # also modify the imeis in the speaker table
    cur.execute('SELECT id, deviceImei FROM speaker')
    speakers = list(cur.fetchall())
    cur.execute('INSERT INTO speaker (id, deviceImei) '+
                'VALUES {} ON DUPLICATE KEY UPDATE deviceImei = VALUES(deviceImei)'
                .format
                    (
                        ','.join([str((x[0], oldImeiToNewImei[x[1]])) for x in speakers])      
                    )
                )

def removeLocation(dest_dir):
    print('Removing location.')
    cur = _db.cursor()
    cur.execute('SELECT id, location FROM session')
    sessions = list(cur.fetchall())
    # idToLoc = {
    #   'sessionId' : 'loc1',
    #   'sessionId' : 'loc2',
    #   ..
    # }
    idToLoc = {}
    for i, s in enumerate(sessions):
        idToLoc[s[0]] = 'loc{}'.format(i+1)

    # write the oldLoc -> newLoc file
    print('Creating hash file for locations.')
    with open(os.path.join(dest_dir, 'locations.tsv'), 'w') as f:
        f.write('sessionId\toldLoc\tnewLoc\n')
        for s in sessions:
            f.write('{}\t{}\t{}\n'.format(s[0], s[1], idToLoc[s[0]]))

    # update our sessions by overwriting the previous ones with our new ones
    # thanks Michiel de Mare, http://stackoverflow.com/questions/3432/multiple-updates-in-mysql
    cur.execute('INSERT INTO session (id, location) '+
                'VALUES {} ON DUPLICATE KEY UPDATE location = VALUES(location)'
                .format
                    (
                        ','.join([str((x[0], idToLoc[x[0]])) for x in sessions])      
                    )
                )

def removeEvaluators(dest_dir):
    print('Removing evaluators.')
    cur = _db.cursor()
    cur.execute('SELECT evaluator FROM evaluation GROUP BY evaluator')
    evaluators = list(cur.fetchall())
    oldToNew = {}
    for i, s in enumerate(evaluators):
        oldToNew[s[0]] = 'evaluator{}'.format(i+1)

    # write the oldEvaluator -> newEvaluator file
    print('Creating hash file for evaluators.')
    with open(os.path.join(dest_dir, 'evaluators.tsv'), 'w') as f:
        f.write('oldEvaluator\tnewEvaluator\n')
        for s in evaluators:
            f.write('{}\t{}\n'.format(s[0], oldToNew[s[0]]))

    # update our evaluators by overwriting the previous ones with our new ones
    for s in evaluators:
        cur.execute('UPDATE evaluation SET evaluator=%s WHERE evaluator=%s',
                    (oldToNew[s[0]], s[0]))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Remove selected personal information from database and filesystem
        (usernames are included in filenames) and replace them with simple unique names (e.g. speaker0).
        Writes the mapping from new values -> old values to files. (to not lose information)""")
    parser.add_argument('rec_path', type=str, help='Path to the recordings, should be the parent folder of all the session_X folders. E.g. /data/eyra/recordings.')
    parser.add_argument('dest_dir', type=str, help='Path to where you want the hashing files saved.')
    parser.add_argument('--retain-speakers', action='store_true', help='Default is to remove speaker names. This flag keeps the speaker names untouched.')
    parser.add_argument('--remove-imei', action='store_true', help='Remove device id\'s/imei\'s.')
    parser.add_argument('--remove-location', action='store_true', help='Remove all location info.')
    parser.add_argument('--remove-evaluators', action='store_true', help='Remove all evaluator names.')
    parser.add_argument('--verbose', '-v', action='store_true', help='A more verbose output.')
    args = parser.parse_args()

    if args.verbose:
        verbose = True

    if args.retain_speakers and not args.remove_imei and not args.remove_location:
        print('These options will mean no changes made to anything. Exiting.')
        exit(0)

    if (input(
'This will modify the database (possibly files) and remove personal information.\
 Be sure to take a backup just in case. Are you sure you want \
 to continue? (y/n)\n') == 'y'):
        run(args.rec_path, args.dest_dir, args.retain_speakers, args.remove_imei, args.remove_location, args.remove_evaluators)