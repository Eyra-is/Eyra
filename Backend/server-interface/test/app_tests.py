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

# File originally created with help from here: http://flask.pocoo.org/docs/0.11/testing/

import os
import unittest
import tempfile
import sys
import json
from unittest.mock import MagicMock

# mv out of test directory and do relative imports from there.
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(newPath)
import app as appMain
sys.path.remove(newPath)
del newPath

class AppTestCase(unittest.TestCase):
    def setUp(self):
        # overwrite some methods in the handlers (the ones with side effects)
        appMain.dbHandler = mockDbHandler()
        appMain.qcHandler = mockQcHandler()

        self.app = appMain.app.test_client()

    def tearDown(self):
        pass

    def test_main(self):
        print('\nIn test main')
        self.assertIsNotNone(self.app)
        # this route only allows GET as a test of server working.
        response = self.app.get('/submit/session')
        self.assertIn(b'GET success baby', response.data)

        self.assertEqual(type(appMain.app.config['MAIN_RECORDINGS_PATH']), type('aString'))
        print('If you have never saved anything to filesystem through Eyra, this test might fail.')
        self.assertTrue(os.path.exists(appMain.app.config['MAIN_RECORDINGS_PATH']))

    def test_submission_routes(self):
        print('\nIn test submission')
        # session
        response = self.app.post('/submit/session', data='{}')
        self.assertNotEqual(response.status_code, 200) # no json data
        response = self.app.post('/submit/session', data=  dict(json='{}'))
        self.assertNotEqual(response.status_code, 200) # no recordings
        # TODO test submitting recordings as multimedia

        # general
        # TODO test urls needing login (like submit/session/{device,instructor})
        #response = self.login('rooney@ru.is', 'suchPass') # gives 500 error for some reason

        # gettokens
        response = self.app.get('/submit/gettokens/0')
        self.assertNotEqual(response.status_code, 200) # error with get for 0 tokens

        # test getting various amounts of tokens
        print('Attention: The following test of \'submit/gettokens/X\' could fail in the unlikely event some ids get chosen twice at random.')
        lengths = [1, 5, 1500]
        for l in lengths:
            response = self.app.get('/submit/gettokens/{}'.format(l))
            tokens = json.loads(response.data.decode('utf-8'))
            print('The \'submit/gettokens/{}\' resulted in: {}'.format(l, len(tokens)))
            if l != lengths[-1]:
                self.assertEqual(len(tokens), l)
            else:
                # the grab tokens isn't accurate. 
                #  a) in case multiple ids are the same, the select in clause won't repeat them
                #  b) some tokens could be invalid meaning they will simply be dropped
                self.assertLessEqual(len(tokens), l)
                self.assertGreater(len(tokens), l - 500) # lets gamble 500 of the same token is extremely unlikely.

    def test_qc_routes(self):
        print('\nIn test qc')
        response = self.app.get('/qc/report/session/0')
        self.assertEqual(response.status_code, 404) # session shouldn't exist (mysql starts count at 1)
        response = self.app.get('/qc/report/session/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('"sessionId": 1', response.data.decode('utf-8'))

    def test_evaluation_routes(self):
        print('\nIn test evaluation')
        # get from set
        response = self.app.get('/evaluation/set/Random/progress/0/count/5')
        sample = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(sample), 5)
        self.assertEqual(type(sample[0][0]), type('aString'))
        self.assertEqual(type(sample[0][1]), type('aString'))

        # submit evaluation
        response = self.app.post('/evaluation/submit/Random', 
            data=dict(json=
                '\
                    [\
                        {\
                            "evaluator": "daphne",\
                            "sessionId": 1,\
                            "recordingFilename": "NOTAREALRECORDING",\
                            "grade": 2,\
                            "comments": "Bad pronunciation",\
                            "skipped": false\
                        },\
                        {\
                            "evaluator": "daphne",\
                            "sessionId": 10,\
                            "recordingFilename": "test2.wav",\
                            "grade": 4,\
                            "comments": "Bad pronunciation",\
                            "skipped": false\
                        }\
                    ]\
                ')
        )
        self.assertEqual(response.status_code, 200)

        # get set info
        response = self.app.get('/evaluation/setinfo/Random')
        self.assertIn('\\u221e', response.data.decode('utf-8')) # \\u221e == ∞

        # get user progress
        response = self.app.get('/evaluation/progress/user/JohnnyBGoode/set/Random')
        self.assertEqual(json.loads(response.data.decode('utf-8'))['progress'], 0)
        response = self.app.get('/evaluation/progress/user/JohnnyBGoode/set/NoOneWouldEver#ComeUpWithThisSetName')
        self.assertEqual(json.loads(response.data.decode('utf-8'))['progress'], 0)

        # get possible sets
        response = self.app.get('/evaluation/possiblesets')
        self.assertIn('Random', response.data.decode('utf-8'))

    # these login/out functions don't work currently.
    def login(self, email, password):
        return self.app.post('auth/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('logout', follow_redirects=True)

def mockDbHandler():
    """
    Returns a MagicMock() with some methods of dbHandler to fit these tests here.
    """
    mockDb = appMain.dbHandler
    mockDb.processEvaluation = MagicMock(return_value=('Success', 200))
    return mockDb

def mockQcHandler():
    """
    Returns a MagicMock() with some methods of qcHandler to fit these tests here.
    """
    mockQc = appMain.qcHandler
    mockQc.getReport = MagicMock(side_effect=[None, dict(sessionId=1, status='started', modules={})])
    return mockQc

if __name__ == '__main__':
    unittest.main()