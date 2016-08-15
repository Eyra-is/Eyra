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

# Quick and dirty file to insert sets for evaluation. The 'test_set.txt' file
# contains the recording filename (without .wav extension) one on each line.

import MySQLdb

dbConst = dict(host='localhost',
    user='root',
    db='recordings_master',
    use_unicode=True,
    charset='utf8')
_db = MySQLdb.connect(**dbConst)


def run():
    with open('test_set.txt', 'r') as f:
        try:
            cur = _db.cursor()

            j = 1
            for line in f:
                print('Processing line: {} ({})'.format(line.rstrip(), j))
                cur.execute('SELECT recording.id FROM recording '+
                            'WHERE recording.filename=%s', (line.rstrip()+'.wav',))
                
                recId = cur.fetchone()[0]
                cur.execute('INSERT INTO evaluation_sets (eval_set, recordingId) '+
                            'VALUES (\'test_set\', %s)', (recId,))
                j += 1
        except MySQLdb.Error as e:
            msg = 'Error inserting utts into set.'
            log(msg, e)
            raise     

        # finally commit if no exceptions
        _db.commit()


if __name__ == '__main__':
    run()
