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
#     Róbert Kjaran <robert@kjaran.com>

import MySQLdb
import os
import sys

# mv out of script directory and do relative imports from server-interface.
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, 'server-interface'))
sys.path.append(newPath)
from config import dbConst # to connect to database
from util import log
sys.path.remove(newPath)
del newPath

def genKaldiDatadir(recordings_path, kaldi_datadir_path):
    """See description, the de-script-ion of the script."""
    _db = MySQLdb.connect(**dbConst)
    SAMPLERATE = 16000
    REC_COUNT_THRESHOLD = 50

    try:
        cur = _db.cursor()
        cur.execute('SELECT recording.id, tokenId, recording.speakerId, sessionId, filename '
                    'FROM ( SELECT speakerId, COUNT(speakerId) '
                    '       AS rCnt FROM recording GROUP BY speakerId ) AS t1, '
                    '     recording WHERE recording.speakerId = t1.speakerId AND t1.rCnt > %s\
                          AND recording.id < 6059', # TEMP ADDITION FOR SHITFIX
                    (REC_COUNT_THRESHOLD,))
        recordings = cur.fetchall()
    except MySQLdb.Error as e:
        msg = 'Error getting recordings' 
        log(msg, e)
        raise

    os.makedirs(kaldi_datadir_path, exist_ok=True)
    # TODO use os.path.join
    text = open('{}/text'.format(kaldi_datadir_path), 'w')
    wavscp = open('{}/wav.scp'.format(kaldi_datadir_path), 'w')
    utt2spk = open('{}/utt2spk'.format(kaldi_datadir_path), 'w')
    spk2utt = open('{}/spk2utt'.format(kaldi_datadir_path), 'w')

    for rec in recordings:
        recId = rec[0]
        tokenId = rec[1]
        speakerId = rec[2]
        sessionId = rec[3]
        filename = rec[4]

        try:
            cur = _db.cursor()
            cur.execute('SELECT inputToken FROM token WHERE id=%s', (tokenId,))
            token = cur.fetchone()
            if token is None:
                raise ValueError('Couldn\'t find token with id={}'.format(tokenId))
            else:
                token = token[0] # fetchone returns tuple
        except MySQLdb.Error as e:
            msg = 'Error getting tokens' 
            log(msg, e)
            raise

        utt_id = '{}-{}'.format(speakerId, recId)
        spkr = str(speakerId)
        full_rec_path = os.path.abspath(os.path.join(
            recordings_path, 
            'session_{}'.format(sessionId), 
            filename))
        print(utt_id, token.lower(), file=text)
        print('{utt_id} sox - -c1 -esigned -r{samplerate} -twav - < {full_rec_path} | '.format(
            utt_id=utt_id, samplerate=SAMPLERATE, full_rec_path=full_rec_path), file=wavscp)
        print(utt_id, spkr, file=utt2spk)

    text.close()
    wavscp.close()
    utt2spk.close()

    os.system('utils/utt2spk_to_spk2utt.pl < {datadir}/utt2spk > {datadir}/spk2utt'.format(datadir=kaldi_datadir_path))
    os.system('utils/validate_data_dir.sh --no-feats {datadir} || utils/fix_data_dir.sh {datadir}'.format(datadir=kaldi_datadir_path))

    spk2utt.close()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Parses our metadata and creates the files necessary for a Kaldi data dir (utt2spk etc.)""")
    parser.add_argument('recordings_path', type=str, help='Path to recordings folder (i.e. /data/eyra/recordings) which includes the session_X folders.')
    parser.add_argument('kaldi_datadir_path', type=str, help='Path to generated kaldi data.')
    args = parser.parse_args()

    genKaldiDatadir(    args.recordings_path, 
                        args.kaldi_datadir_path
    )
