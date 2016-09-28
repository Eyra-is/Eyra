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

# TODO write tests for more aspects of the marosijo module, not just the analyzer.

# File originally created with help from here: http://flask.pocoo.org/docs/0.11/testing/

import os
import unittest
import tempfile
import sys
import json
from unittest.mock import MagicMock

# mv out of test directory and do relative imports from there.
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir))
sys.path.append(newPath)
import qc.modules.MarosijoModule.MarosijoModule as marosijo
sys.path.remove(newPath)
del newPath

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.marosijo = marosijo.MarosijoTask()

    def tearDown(self):
        pass

    def test_marosijo_analyzer(self):
        common = self.marosijo.common

        # test _alignHyp
        oov = common.symbolTable['<UNK>']
        refs_hyps = [
            ('the dog jumped across',
             'dog j u m p across',
             [1, -1, -1, -1, -1, 3]),
            ('dog ate the dog in dog',
             'dog ate',
             [0, 1]),
            ('dog ate the dog in dog ate',
             'in dog',
             [4, 5]),
            ('the dog ate the dog and',
             'the d u n g dog and',
             [0, -1, -1, -1, -1, 4, 5]),
            ('12657 12768 19593 543',
             '27903 27920 27923 27929 27905 27901 27902 27934 27943 27901',
             [-1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1]),
            # test marking oov, <UNK> as -1, this number, e.g. 25140, must match <UNK> in symbol table
            ('12657 12768 19593 543 {oov} {oov}'.format(oov=oov),
             '12657 12768 {oov} {oov} {oov}'.format(oov=oov),
             [0, 1, -1, -1, -1]),
            # edge cases
            ('{oov}'.format(oov=oov),
             '{oov}'.format(oov=oov),
             [-1]),
            ('{oov}'.format(oov=oov),
             '',
             []),
            #
            ('out of out of out of out of',
             'out of out of out of out of',
             [0,  1, 2,  3, 4,  5, 6,  7]),
            ('out of the out of the out of',
             'out of the out out',
             [0,  1, 2,  3,  6])
        ]

        for rh in refs_hyps:
            ref = rh[0].split()
            hyp = rh[1].split()
            anal = marosijo.MarosijoAnalyzer(hyp, ref, common)
            self.assertEqual(anal._alignHyp(hyp, ref), rh[2])
            print(anal._alignHyp(hyp, ref))

if __name__ == '__main__':
    unittest.main()
