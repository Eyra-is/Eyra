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

        # 27901 - 27943 are the phonemes
        # average phoneme length: 9
        # these tests are specific to the icelandic data, since phoneme overlap and more is tested
        # TODO automate these tests (locate the phonemes, and use random words with some overlap from lexicon)
        oov = common.symbolTable['<UNK>']
        refs_hyps = [
            # test some generic stuff
            # bunki / fylkis / hlíðarbraut / athuga
            # p ʏ ɲ̊ c ɪ / f ɪ l̥ c ɪ s / l̥ i ð a r p r ø y t / a t h ʏ ɣ a         27
            ('3624 7363 10345 1479',                                             # ref
            # !a    !u    !n    fylkis  !p !ɔ    !s hlíðarbraut !t !h    !ɛ
             '27903 27935 27920 7363 27928 27926 27932 10345 27933 27911 27909', # hyp
             [-1, -1, -1, 1, -1, -1, -1, 2, -1, -1, -1],                         # alignHyp
             2/4 + 2/6*1/4,                                                      # accuracy
             15/27),                                                             # phone_acc
            # kaupmenn / kerti / rögn / áhyggjufullur
            # kʰ ø y p m ɛ n / cʰ ɛ r̥ t ɪ / r œ k n / a u h ɪ c ʏ f ʏ t l ʏ r       28
            ('12657 12768 19593 543',
            # !a    !n    !p    !m    !ɛ    kerti !tʰ   !ɲ    !ɪ
             '27903 27920 27928 27918 27909 12768 27934 27943 27901',
             [-1,   -1,   -1,   -1,   -1,   1,   -1,   -1,   -1],
             1/4 + 3/7*1/4 + 1/16*2*1/4,
             9/28),
            # kaupmenn / kerti / rögn / áhyggjufullur
            # kʰ ø y p m ɛ n / cʰ ɛ r̥ t ɪ / r œ k n / a u h ɪ c ʏ f ʏ t l ʏ r       28
            ('12657 12768 19593 543',
            # !a    !n    !ŋ̊   !pʰ   !cʰ   !ɪ    !ɲ̊   !tʰ   !ɲ    !ɪ
             '27903 27920 27923 27929 27905 27901 27902 27934 27943 27901',
             [-1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1],
             3/28,
             3/28),
            # test that the error caps at -1/2 * wc (in this case -0.5*2)
            # kaupmenn / rögn / kerti/ áhyggjufullur
            # kʰ ø y p m ɛ n / r œ k n / cʰ ɛ r̥ t ɪ / a u h ɪ c ʏ f ʏ t l ʏ r        28
            ('12657 19593 12768 543',
            # !a    !tʰ   !n̥   !ɪ    !ɲ    !a    !tʰ   !n̥   !ɪ    !ɲ
             '27903 27934 27921 27901 27943 27903 27934 27921 27901 27943 \
              27903 27934 27921 27901 27943 27903 27934 27921 27901 27943 \
              27903 27934 27921 27901 27943 27903 27934 27921 27901 27943 \
              12768 27934 27943 27901',
            # kerti !tʰ   !ɲ    !ɪ
             [-1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,
              -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,
              -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,
               2,   -1,   -1,   -1],
             1/4 + -0.5*2/4 + 1/12*1/4,
             0),
            # test that it correctly gives error when there are no words to compare to
            # bunki / fylkis / hlíðarbraut / athuga
            # p ʏ ɲ̊ c ɪ / f ɪ l̥ c ɪ s / l̥ i ð a r p r ø y t / a t h ʏ ɣ a
            ('3624 7363 10345 1479',
            # !a    !u    !n    fylkis  !p !ɔ    !s x3  hlíðarbraut !t !h    !ɛ
             '27903 27935 27920 7363 27928 27926 27932 27928 27926 27932 27928 27926 27932 27928 27926 27932 10345 27933 27911 27909',
             [-1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2, -1, -1, -1],
             2/4 - 0.5*1/4 + 2/6*1/4),
            # test marking oov, <UNK> as -2, this number, e.g. 25140, must match <UNK> in symbol table
            ('12657 12768 19593 543',
             '12657 12768 {oov} {oov} {oov}'.format(oov=oov),
             [0, 1, -2, -2, -2],
             2/4),
            # edge cases
            ('12657',
             '{oov}'.format(oov=oov),
             [-2],
             0),
            ('{}'.format(oov),
             '27903 27935',
             [-1, -1],
             0),
            ('{}'.format(oov),
             '',
             [],
             0),
            ('{}'.format(oov),
             '{}'.format(oov),
             [-2],
             0),
            # test align hyp a bit
            ('8591 10022 3683 8591 2663 8591',
             '8591 10022',
             [0, 1],
             2/6),
            ('10021 5257 3751 10021 5789 10021 5257',
             '5789 10021',
             [4, 5],
             2/7),
            #
            ('3365 3373 3365 3373 3365 3373 3365 3373',
             '3365 3373 3365 3373 3365 3373 3365 3373',
             [0,  1, 2,  3, 4,  5, 6,  7],
             1),
            ('3365 3373 3416 3365 3373 3416 3365 3373',
             '3365 3373 3416 3365 3365',
             [0,  1, 2,  3,  6],
             5/8),
            # fyrst með jurtum og galdri en síðan með oddhvössu járni
            # f ɪ r̥ s t 
            ('7435 15985 12381 17716 7520 4969 20565 15985 17597 12159',
            #    !f !ɪ    !s
             '27910 27901 27932 15985 12381 17716 7520 4969 20565 17597 12159',
             [-1, -1, -1, 1, 2, 3, 4, 5, 6, 8, 9],
             3/5*1/10 + 8/10),
            # ég
            # j ɛ ɣ
            ('4501 5455 26062 32 4501 10587 23149 20809',
            # !m
             '27918 4501 5455 26062 32 4501 10587 23149 20809',
             [-1, 0, 1, 2, 3, 4, 5, 6, 7],
             1)
        ]

        for rh in refs_hyps:
            ref = rh[0].split()
            hyp = rh[1].split()
            anal = marosijo.MarosijoAnalyzer(hyp, ref, common)
            # test _alignHyp
            self.assertEqual(anal._alignHyp(hyp, ref), rh[2])
            # test _calculateAccuracy
            self.assertAlmostEqual(anal._calculateAccuracy(), rh[3])

        for rh in refs_hyps[:4]:
            ref = rh[0].split()
            hyp = rh[1].split()
            anal = marosijo.MarosijoAnalyzer(hyp, ref, common)
            self.assertAlmostEqual(anal._calculatePhoneAccuracy(), rh[4])

if __name__ == '__main__':
    unittest.main()
