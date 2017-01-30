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

        # e.g. 32866 - 32908 are the phonemes
        # average phoneme length: 9
        # these tests are specific to the icelandic data, since phoneme overlap and more is tested
        # TODO automate these tests more (use random words with some overlap from lexicon)
        oov = common.symbolTable['<UNK>']
        # locate phonemes
        basePhone = int(common.symbolTable['</s>']) + 1
        endPhone = int(common.symbolTable['#00'])
        phones = [basePhone + i for i in range(0, endPhone - basePhone)]
        refs_hyps = [
            # test some generic stuff
            # bunki / fylkis / hlíðarbraut / athuga
            # p ʏ ɲ̊ c ɪ / f ɪ l̥ c ɪ s / l̥ i ð a r p r ø y t / a t h ʏ ɣ a         27
            ('4257 8656 12171 1736',                                             # ref
            # !a !u !n fylkis !p !ɔ !s hlíðarbraut !t !h !ɛ
             '{} {} {} 8656 {} {} {} 12171 {} {} {}'
             .format(phones[2], phones[34], phones[19], phones[27], phones[25], phones[31], phones[32], phones[10], phones[8]), # hyp
             [-1, -1, -1, 1, -1, -1, -1, 2, -1, -1, -1],                         # alignHyp
             2/4 + 2/6*1/4,                                                      # hybrid
             1/4,                                                                # wer
             15/27),                                                             # phone_acc
            # kaupmenn / kerti / rögn / áhyggjufullur
            # kʰ ø y p m ɛ n / cʰ ɛ r̥ t ɪ / r œ k n / a u h ɪ c ʏ f ʏ t l ʏ r       28
            ('14932 15066 23070 640',
            # !a !n !p !m !ɛ kerti !tʰ !ɲ !ɪ
             '{} {} {} {} {} 15066 {} {} {}'
             .format(phones[2], phones[19], phones[27], phones[17], phones[8], phones[33], phones[42], phones[0]),
             [-1,   -1,   -1,   -1,   -1,   1,   -1,   -1,   -1],
             1/4 + 3/7*1/4 + 1/16*2*1/4,
             1/4,
             9/28),
            # kaupmenn / kerti / rögn / áhyggjufullur
            # kʰ ø y p m ɛ n / cʰ ɛ r̥ t ɪ / r œ k n / a u h ɪ c ʏ f ʏ t l ʏ r       28
            ('14932 15066 23070 640',
            # !a    !n    !ŋ̊   !pʰ   !cʰ   !ɪ    !ɲ̊   !tʰ   !ɲ    !ɪ
             '{} {} {} {} {} {} {} {} {} {}'
             .format(phones[2], phones[19], phones[22], phones[28], phones[4], phones[0], phones[1], phones[33], phones[42], phones[0]),
             [-1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1],
             3/28,
             0.0,
             3/28),
            # test that the error caps at -1/2 * wc (in this case -0.5*2)
            # kaupmenn / rögn / kerti/ áhyggjufullur
            # kʰ ø y p m ɛ n / r œ k n / cʰ ɛ r̥ t ɪ / a u h ɪ c ʏ f ʏ t l ʏ r        28
            ('14932 23070 15066 640',
            # !a !tʰ !n̥  !ɪ !ɲ !a  !tʰ  !n̥ !ɪ !ɲ
             '{} {} {} {} {} {} {} {} {} {} \
              {} {} {} {} {} {} {} {} {} {} \
              {} {} {} {} {} {} {} {} {} {} \
              15066 {} {} {}'
              .format(
                phones[2], phones[33], phones[20], phones[0], phones[42], phones[2], phones[33], phones[20], phones[0], phones[42],
                phones[2], phones[33], phones[20], phones[0], phones[42], phones[2], phones[33], phones[20], phones[0], phones[42],
                phones[2], phones[33], phones[20], phones[0], phones[42], phones[2], phones[33], phones[20], phones[0], phones[42],
                phones[33], phones[42], phones[0]
              ),
            # kerti !tʰ   !ɲ    !ɪ
             [-1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,
              -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,
              -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,
               2,   -1,   -1,   -1],
             1/4 + -0.5*2/4 + 1/12*1/4,
             1/4,
             0),
            # test that it correctly gives error when there are no words to compare to
            # bunki / fylkis / hlíðarbraut / athuga
            # p ʏ ɲ̊ c ɪ / f ɪ l̥ c ɪ s / l̥ i ð a r p r ø y t / a t h ʏ ɣ a
            ('4257 8656 12171 1736',
            # !a    !u    !n    fylkis  !p !ɔ    !s x3  hlíðarbraut !t !h    !ɛ
             '{} {} {} 8656 {} {} {} {} {} {} {} {} {} {} {} {} 12171 {} {} {}'
             .format(phones[2], phones[34], phones[19], phones[27], phones[25], phones[31], phones[27], phones[25], phones[31], phones[27], phones[25], phones[31], phones[27], phones[25], phones[31], phones[32], phones[10], phones[8]),
             [-1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2, -1, -1, -1],
             2/4 - 0.5*1/4 + 2/6*1/4,
             1/4),
            # test marking oov, <UNK> as -2, this number, e.g. 25140, must match <UNK> in symbol table
            ('14932 15066 23070 640',
             '14932 15066 {oov} {oov} {oov}'.format(oov=oov),
             [0, 1, -2, -2, -2],
             2/4,
             2/4),
            # edge cases
            ('14932',
             '{oov}'.format(oov=oov),
             [-2],
             0,
             0.0),
            ('{}'.format(oov),
             '{} {}'
             .format(phones[2], phones[34]),
             [-1, -1],
             0,
             0.0),
            ('{}'.format(oov),
             '',
             [],
             0,
             0.0),
            ('{}'.format(oov),
             '{}'.format(oov),
             [-2],
             0,
             0.0),
            # test align hyp a bit
            ('8591 10022 3683 8591 2663 8591',
             '8591 10022',
             [0, 1],
             2/6,
             2/6),
            ('10021 5257 3751 10021 5789 10021 5257',
             '5789 10021',
             [4, 5],
             2/7,
             2/7),
            #
            ('3365 3373 3365 3373 3365 3373 3365 3373',
             '3365 3373 3365 3373 3365 3373 3365 3373',
             [0,  1, 2,  3, 4,  5, 6,  7],
             1,
             1.0),
            ('3365 3373 3416 3365 3373 3416 3365 3373',
             '3365 3373 3416 3365 3365',
             [0,  1, 2,  3,  6],
             5/8,
             5/8),
            # fyrst með jurtum og galdri en síðan með oddhvössu járni
            # f ɪ r̥ s t 
            ('8744 18841 14591 20867 8841 5879 24211 18841 20717 14329',
            # !f !ɪ !s
             '{} {} {} 18841 14591 20867 8841 5879 24211 20717 14329'
             .format(phones[9], phones[0], phones[31]),
             [-1, -1, -1, 1, 2, 3, 4, 5, 6, 8, 9],
             3/5*1/10 + 8/10,
             8/10),
            # ég
            # j ɛ ɣ
            ('5340 5455 26062 32 5340 10587 23149 20809',
            # !m
             '{} 5340 5455 26062 32 5340 10587 23149 20809'
             .format(phones[17]),
             [-1, 0, 1, 2, 3, 4, 5, 6, 7],
             1,
             7/8)
        ]

        for rh in refs_hyps:
            ref = rh[0].split()
            hyp = rh[1].split()
            # print('Ref: {}, hyp: {}'.format(ref, hyp))
            anal = marosijo.MarosijoAnalyzer(hyp, ref, common)
            # test _alignHyp
            self.assertEqual(anal._alignHyp(hyp, ref), rh[2])
            # test _calculateHybridAccuracy
            hybrid, wer = anal._calculateHybridAccuracy()
            # hybdid
            self.assertAlmostEqual(hybrid, rh[3])
            # wer
            self.assertAlmostEqual(wer, rh[4])

        for rh in refs_hyps[:4]:
            ref = rh[0].split()
            hyp = rh[1].split()
            anal = marosijo.MarosijoAnalyzer(hyp, ref, common)
            self.assertAlmostEqual(anal._calculatePhoneAccuracy(), rh[5])

if __name__ == '__main__':
    unittest.main()
