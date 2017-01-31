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
#     Róbert Kjaran <robert@kjaran.com>
#     Matthias Petursson <oldschool01123@gmail.com>

import os
import json
import tempfile
import sys
import uuid
import itertools
from functools import partial

import redis
import sh
from celery import Task
import numpy as np

import os.path
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.append(newPath)
import celery_config
from util import errLog, log, isWavHeaderOnly
sys.path.remove(newPath)
del newPath


_DEFAULT_KALDI_ROOT = os.path.abspath(
    os.path.join(__file__, '../../../../../../Local/opt/kaldi-trunk'))


# Kudos to http://stackoverflow.com/users/95810/alex-martelli for
# http://stackoverflow.com/a/3233356 which this is based on
import collections
def update(d, u):
    """Recursively updates nested dicts. Lists are NOT updated, they are extended
    with new list value. MUTATES `d`.

    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        elif isinstance(v, list):
            r = d.get(k, []).extend(v)
        else:
            d[k] = u[k]
    return d


class MarosijoError(Exception):
    pass


class MarosijoAnalyzer(object):
    """MarosijoAnalyzer
    ===================

    Does analysis of decoded output, given reference and hypothesis
    string.

    """
    def __init__(self, hypothesis, reference, common):
        self.reference = reference
        self.hypothesis = hypothesis
        self.common = common # used to grab info like symbolTable

    @staticmethod
    def _levenshteinDistance(hyp, ref, cost_sub=1, cost_del=1, cost_ins=1):
        '''
        Returns the minimum edit distance (Levenshtein distance) between
        sequences `ref` and `hyp`, and the corresponding Levenshtein matrix.

        '''
        m, n = len(hyp)+1, len(ref)+1
        d = np.zeros((m, n))
        d[1:, 0] = range(1, m)
        d[0, 1:] = range(1, n)

        edits = []
        for j in range(1, n):
            for i in range(1, m):
                del_ = d[i-1, j] + cost_del
                ins_ = d[i, j-1] + cost_ins
                sub_ = d[i-1, j-1]
                sub_ += cost_sub if hyp[i-1] != ref[j-1] else 0
                d[i, j] = min(del_, ins_, sub_)

        return int(d[-1, -1]), d

    @staticmethod
    def levenshteinDistance(a, b):
        d, _ = _levenshteinDistance(a, b)
        return d

    @staticmethod
    def shortestPath(d):
        """Returns the shortest sequence of edits in the levenshtein matrix `d`

        """
        SUBCORR, INS, DEL = 0, 1, 2
        nDel, nIns, nSub, nCor = 0, 0, 0, 0
        revEditSeq = []
        i, j = np.shape(d)
        i, j = i-1, j-1
        # Special case for only empty inputs
        if i == 0 and j != 0:
            nDel = j
            revEditSeq = ['D'] * nDel
        elif i != 0 and j == 0:
            nIns = i
            revEditSeq = ['I'] * nIns
        elif i != 0 and j != 0:
            outOfBounds = False
            while not outOfBounds:
                del_ = d[i, j-1] if i >= 0 and j > 0 else np.inf
                ins = d[i-1, j] if i > 0 and j >= 0 else np.inf
                subOrCor = d[i-1, j-1] if i > 0 and j > 0 else np.inf
                idxMin = np.argmin([subOrCor, ins, del_])
                if idxMin == DEL:
                    j -= 1
                    nDel += 1
                    revEditSeq.append('D')
                elif idxMin == INS:
                    i -= 1
                    nIns += 1
                    revEditSeq.append('I')
                elif idxMin == SUBCORR:
                    if d[i-1, j-1] != d[i, j]:
                        nSub += 1
                        revEditSeq.append('S')
                    else:
                        nCor += 1
                        revEditSeq.append('C')
                    i, j = i-1, j-1
                if i == 0 and j == 0:
                    outOfBounds = True
        return revEditSeq[::-1], nCor, nSub, nIns, nDel

    def _computeEdits(self):
        self._distance, self.d = self._levenshteinDistance(self.hypothesis, self.reference)
        self.seq, self.nC, self.nS, self.nI, self.nD = self.shortestPath(self.d)

    def _calculateHybridAccuracy(self) -> (float, float):
        """
        Hybrid accuracy is some sort of metric, attempts to locate correct words.
        E.g. ref: the dog jumped over the fence
             hyp: the /c/o/d/ ran over the tent
        would result in an accuracy of 3/6 + 1/3*1/6 = 0.555 for getting the, over, the and a 
        single phoneme from dog correct.
        Extra words are also treated as errors, e.g.
             ref: the dog jumped over the fence
             hyp: /i/n/s/e/r/t/i/o/n/ the dog jumped over the fence
        would divide insertion by the average phoneme count of words (if 5) and then
        accuracy would be 6 - 5/4 / 6 = 4.75/6 = 0.792
        TODO not make this average, but use an actual phoneme 2 grapheme and locate the words
        Words in middle, are compared to phonemes of the words from ref, and a ratio of correct
        phonemes calculated from that.

        accuracy c [0,1]

        also calculates regular WER (done here since the align hyp computation is needed and
        has already been done here) on a word level grouping hyp phonemes into words

        e.g. ref: the dog jumped over the fence
             hyp: the /c/o/d/ ran over the tent
        would result in a wer of 3/6 = 0.5 (3 substitutions)

        return:
            (hybrid, wer)
        """

        oovId = self.common.symbolTable['<UNK>']

        hyp = self.hypothesis
        ref = self.reference

        # convert all words in ref to phonemes
        try:
            ref_phones = [self.common.lexicon[self.common.symbolTableToInt[x]] for x in ref]
        except KeyError as e:
            # word in ref not in lexicon, abort trying to convert it to phonemes
            log('Warning: couldn\'t find prompt words in lexicon or symbol table (grading 0.0), prompt: {}'.format(ref))
            return (0.0, 0.0)

        aligned = self._alignHyp(hyp, ref)
        ali_no_oov = [x for x in aligned if x != -2] # remove oov for part of our analysis
        hyp_no_oov = [x for x in hyp if x != oovId]

        # mark positions of recognized words, e.g. rec_words = [0, 3, 5]
        rec_words = []
        # mark all strings of -1's (meaning we have phonemes inserted)
        minus_ones = [] # minus_ones = [(1,3), (4,5), ..], i.e. tuples of linked sequences of -1's
        inSequence = False
        seq = [] # partial sequence
        for i, a in enumerate(ali_no_oov):
            if a == -1 and not inSequence:
                inSequence = True
                seq.append(i)
            if a != -1 and inSequence:
                inSequence = False
                seq.append(i)
                minus_ones.append(seq)
                seq = []
            # if we have -1's at the end of ali_no_oov
            if i == len(ali_no_oov) - 1 and a == -1 and inSequence:
                seq.append(len(ali_no_oov))
                minus_ones.append(seq)
            if a >= 0:
                rec_words.append(a)

        # for each sequence of -1's calculate phoneme overlap with corresponding words.
        # e.g. if ref: the cat jumped
        #         hyp: the cat j u m p
        # we would calc the overlap of 'j u m p e d' with 'j u m p'
        ratios = [] # len(ratios) == len(minus_ones) ratios of each sequence phoneme overlap (contribution to word error rate)

        wer_insertions = 0

        for seq in minus_ones:
            # convert seq to phoneme list, grab e.g. !h from symbolTable and remove ! to match with lexicon
            seq_phones = [self.common.symbolTableToInt[x][1:] for x in hyp_no_oov[seq[0] : seq[1]]]
            ref_phones_range = () # which indices in ref_phones do we want to compare to? (which words)
            # figure out which words we should compare each phoneme sequence with
            # find out if we are a -1 sequence in the beginning, middle or end of the hyp
            if seq[0] == 0:
                # beginning, look at all words up to the first recognized word
                if rec_words:
                    ref_phones_range = (0, rec_words[0])
                else:
                    # no recognized words, compare to entire ref
                    ref_phones_range = (0, len(ref_phones))
            elif seq[-1] == len(hyp_no_oov):
                # end, look at words from last recognized word
                ref_phones_range = (rec_words[-1]+1, len(ref_phones))
            else:
                # middle, look at words between recognized words to the left&right of this sequence
                # since this is neither beginning or end, we know we have recognized words on both sides
                # e.g. aligned: [0, 1, -1, -1, -1, 4]
                # we want to look at words ref[2:4]
                ref_phones_range = (ali_no_oov[seq[0]-1]+1, ali_no_oov[seq[1]])
            
            hybridPenalty = 1.5
            if ref_phones_range[1] - ref_phones_range[0] > 0:
                # use formula
                # (1 - min(ed/N, hybridPenalty))*wc
                # meaning, if edit distance (levenshtein)
                # is =N (number of phonemes in our attempted words to match (from ref_phones)) 
                # we get a score of zero for this sequence.
                # If edit distance is more (e.g. our aligner inserted more phonemes than are in
                # the reference), we can get a penalty for at most (1-hybridPenalty)*ref word count
                # for the entire sequence.
                N = sum([len(ref_phones[i]) for i in range(ref_phones_range[0], ref_phones_range[1])])
                ed, _ = self._levenshteinDistance(seq_phones, 
                                                  list(
                                                    itertools.chain.from_iterable(
                                                        ref_phones[ref_phones_range[0] : ref_phones_range[1]])
                                                  ))

                ratio = 1 - min(ed / N, hybridPenalty)
                normalized_ratio = ratio*(ref_phones_range[1] - ref_phones_range[0])
                ratios.append(normalized_ratio)
            else:
                # no words to compare to (empty interval this seq compares to)
                # attempt to attempt to give some sort of minus penalty
                # in similar ratio to the one above (if hybridPenalty=1.5 then at most -1/2*wc)
                # use average phoneme count from lexicon, and give at most
                # an error of 1/2 that. For example if avg=5 and our seq has
                # 11 phonemes we give an error of -1/2 * floor(11/5) = -1
                ratios.append((1 - hybridPenalty) * int((seq[1]-seq[0]) / self.common.avgPhonemeCount))

                wer_insertions += 1

        hybrid = max((len(rec_words) + sum(ratios)) / len(ref) , 0)
        # WAcc = (H - I)/N
        # https://en.wikipedia.org/wiki/Word_error_rate
        wer    = (len([x for x in aligned if x >= 0]) - wer_insertions) / len(ref)

        return (hybrid, wer)


    def _calculatePhoneAccuracy(self):
        """
        Similar to _calculateHybridAccuracy, except uses phonemes only.

        Converts ref and hyp to phonemes and does a direct edit distance on the entire thing.

        phone_accuracy c [0,1]
        """
        oovId = self.common.symbolTable['<UNK>']

        hyp = self.hypothesis
        ref = self.reference

        # convert all words in ref to phonemes, excluding oov
        try:
            ref_phones = [self.common.lexicon[self.common.symbolTableToInt[x]] for x in ref if x != oovId]
        except KeyError as e:
            # word in ref not in lexicon, abort trying to convert it to phonemes
            log('Warning: couldn\'t find prompt words in lexicon or symbol table (grading with 0.0), prompt: {}'.format(ref))
            return 0.0

        # convert all words in hyp to phonemes
        hyp_phones = []
        for x in hyp:
            try:
                hyp_phones.append(self.common.lexicon[self.common.symbolTableToInt[x]])
            except KeyError as e:
                # word in hyp not in lexicon, must be a phoneme, in which case just append it and remove the !
                hyp_phones.append([self.common.symbolTableToInt[x][1:]])

        ref_phones = list(itertools.chain.from_iterable(ref_phones))
        hyp_phones = list(itertools.chain.from_iterable(hyp_phones))

        N = len(ref_phones)
        ed, _ = self._levenshteinDistance(hyp_phones, 
                                          ref_phones)

        try:
            ratio = 1 - min(ed / N, 1)
        except ZeroDivisionError as e:
            ratio = 0.0

        return ratio

    def _alignHyp(self, hyp, ref) -> list:
        """
        Attempts to enumerate the hypothesis in some smart manner. E.g.

        ref:    the dog jumped    across
        hyp:        dog /j/u/m/p/ across
        output:     1   -1-1-1-1  3

        Where /j/u/m/p/ represents 4 phonemes inserted instead of jumped and
        these would usually be the integer ids of the words.
        Output is the indices in ref the words in hyp correspond to.

        Parameters:
            hyp     list with the integer ids of the hyp words
            ref     same as hyp with the reference

        Pairs the hypotheses with the index of correct words in the reference. 
        -1 for hypotheses words not in ref (should only be phonemes)
        -2 if hyp word is oov <UNK>.

        Would have used align-text.cc from Kaldi, but it seemed to not perform well
        with all the inserted phonemes (on a very informal check).

        Better description of the algorithm used:
            TO DO WRITE DESC
        """

        # private functions to _alignHyp
        def _wordsBetween(aligned, idx):
            """
            Attempts to see if there are any words between
            the current idx and the last matched word in hyp, 
            and no word in between it in the ref.
            E.g.
                ref: joke about stuff
                hyp: joke and go to stuff

            With: aligned = [0, -1, -1, -1]
                  idx     = 2
            Would result in False, since "and go to" could be the aligners interpretation of about.

                ref: go to France
                hyp:    to five France

            With: aligned = [1, -1]
                  idx     = 2
            Would result in True, since "five" is between to and France
            """
            newAligned = [x for x in aligned if x != -1] # remove -1's
            try:
                lastMatch = newAligned[-1]
            except IndexError as e:
                return False # return false if no recognized word

            if idx - lastMatch > 1:
                return False

            # if we have some -1's after our last match, return true
            if aligned.index(lastMatch) != len(aligned) - 1:
                return True

            return False

        def _isLater(idx, ref):
            """
            Checks to see if ref[idx] is repeated in ref somewhere later,
            and in which case return the later idx.

            Returns -1 if ref[idx] is not repeated.
            """
            refSlice = ref[idx:]
            refSlice[0] = -1
            try:
                return refSlice.index(ref[idx]) + idx
            except ValueError as e:
                return -1

        def _isEarlier(idx, ref):
            """
            Checks to see if ref[idx] is repeated in ref somewhere earlier,
            and in which case return the earlier idx.

            Returns -1 if ref[idx] is not earlier.
            """
            upToIdx = ref[0:idx+1]
            isEarlier = _isLater(0, upToIdx[::-1]) # isEarlier === isLater(new idx, reversed list)
            return len(upToIdx) - isEarlier - 1 if isEarlier != -1 else -1

        oovId = self.common.symbolTable['<UNK>']
        refC = list(ref) # ref copy
        aligned = []
        for h in hyp:
            try:
                if h == oovId:
                    aligned.append(-2)
                    continue

                idx = refC.index(h)
                # handle cases with multiple instances of the same word
                # in case our hypothesised index in the hyp is lower than 
                # some idx in aligned, we know that cannot be, so the only
                # chance is that it is the same word later in the hyp (or not there)
                # In addition, if we see 1 or more words (like dung in the example)
                # which could have been the interpretation of dog, we assume it is the
                # second instance of the word (if present, otherwise assume first instance).
                # e.g. 
                #    ref: the dog ate the dog
                #    hyp: the dung dog
                #    res:   0   -1   4
                refC[idx] = -1 # remove word from ref if we match, in case we have multiple of the same
                while True:
                    try:
                        if any(idx < x for x in aligned) or _wordsBetween(aligned, idx):
                            idx = refC.index(h)
                            refC[idx] = -1
                        else:
                            break
                    except ValueError as e:
                        break
            except ValueError as e:
                idx = -1
            aligned.append(idx)
        # do a second pass
        # if the aligned array is not strictly non-decreasing, fix it
        # e.g. if aligned = [0, -1, -1, 3, 2]
        # see if the one marked 2 isn't supposed to be the same word later in ref
        # this could be problematic if the same 2 words are repeated twice,
        # and possibly if the same word is repeated 3 times as well
        prevA = -sys.maxsize
        for i, a in enumerate(aligned):
            if a < 0:
                continue
            if a <= prevA:
                # we have decreasing
                newIdx = _isLater(a, ref)
                if newIdx != -1:
                    aligned[i] = newIdx
                else:
                    # now see if the 3 in the example above shouldn't be earlier
                    newIdx = _isEarlier(prevA, ref)
                    if newIdx != -1 and newIdx not in aligned:
                        aligned[i-1] = newIdx
                    else:
                        raise MarosijoError('Error: couldn\'t align {} with hyp: {} and ref: {} and aligned: {}'
                            .format(ref[a], hyp, ref, aligned))
            prevA = a

        return aligned

    def editSequence(self):
        """Returns sequence of edits as an iterable

        'C' for correct, 'S' for substitution, 'I' for insertion and
        'D' for deletions.

        """
        if not hasattr(self, 'seq'):
            self._computeEdits()
        return self.seq

    def edits(self):
        """Returns dict with edit counts

        """
        if not hasattr(self, 'nC'):
            self._computeEdits()
        return {'correct': self.nC, 'sub': self.nS, 'ins': self.nI,
                'del': self.nD, 'distance': self._distance}

    def details(self) -> '{hybrid: int\
            phone_acc: int\
            wer: int\
            onlyInsOrSub: bool\
            correct: int\
            sub: int\
            ins: int\
            del: int\
            startdel: int\
            enddel: int\
            extraInsertions: int\
            empty: bool\
            distance: int}':
        """Returns dict with details of analysis

        Distance (and the rest of the stats excluding hybrid) is calculated on a 
        mixture of word/phoneme level, since phonemes are words from this aligner.
        """

        res = self.edits()
        seq = self.editSequence()
        details = {'empty': False, 'onlyInsOrSub': False,
                   'enddel': 0, 'startdel': 0, 'extraInsertions': 0}
        details.update(res)
        details.update(ops=seq)

        details['hybrid'], details['wer'] = self._calculateHybridAccuracy()
        details['phone_acc'] = self._calculatePhoneAccuracy()

        if not any([res['correct'], res['sub'], res['ins']]):
            # 1. Only deletions (hyp empty)?
            details['empty'] = True
        elif (any([res['ins'], res['sub']]) and not
              any([res['correct'], res['ins']])):
            # 2. Only insertions/substitutions?
            details['onlyInsOrSub'] = True
        else:
            # 2. Start/end deletions?
            for op in seq[::-1]:
                if op.upper() == 'D':
                    details['enddel'] += 1
                else: break
            for op in seq:
                if op.upper() == 'D':
                    details['startdel'] += 1
                else: break
            if (len(self.reference) == res['correct'] and res['ins'] and
                not any([res['sub'], res['del']])):
                details['extraInsertions'] = res['ins']

        return details

    def distance(self):
        if not hasattr(self, '_distance'):
            self._computeEdits()
        return self._distance

class MarosijoCommon:
    """MarosijoCommon
    ==================

    Paths, data and other settings for the MarsijoModule

    """
    _REQUIRED_FILES = ('tree', 'acoustic_mdl', 'symbol_tbl',
                       'lexicon_fst', 'disambig_int', 'oov_int',
                       'sample_freq', 'phone_lm', 'lexicon.txt')

    #: Not required to exist when compiling graphs, obviously.
    _REQUIRED_FILES_AFTER_COMPILE = ('graphs.scp',)

    def __init__(self, modelPath=None, downsample=False, graphs=True):
        """
        Parameters:

          modelPath    Path to directory containing model files.
                       Should contain the following files: tree,
                       acoustic_mdl, symbol_tbl, lexicon_fst,
                       disambig_int, unk_int, sample_freq.  These
                       files are generated by
                       ../scripts/train_acoustic_model.sh

        """
        if modelPath is None:
            modelPath = os.path.join(os.path.dirname(__file__), 'local/')
        self.modelPath = os.path.abspath(modelPath)
        self._validateModel(self.modelPath, graphs=graphs)
        self.downsample = downsample

        mkpath = partial(os.path.join, self.modelPath)
        self.treePath = mkpath('tree')
        self.acousticModelPath = mkpath('acoustic_mdl')
        self.symbolTablePath = mkpath('symbol_tbl')
        self.lexiconFstPath = mkpath('lexicon_fst')
        self.disambigIntPath = mkpath('disambig_int')
        self.oovIntPath = mkpath('oov_int')
        #: File contains sample freq of acoustic model
        self.sampleFreqPath = mkpath('sample_freq')
        self.phoneLmPath = mkpath('phone_lm')
        self.lexiconTxtPath = mkpath('lexicon.txt')

        if graphs:
            self.graphsScpPath = mkpath('graphs.scp')

        with open(self.oovIntPath) as f_:
            self.oov = int(f_.read().strip())

        with open(self.sampleFreqPath) as f_:
            self.sampleFreq = int(f_.read().strip())

        with open(self.disambigIntPath) as f_:
            self.disambigInt = [int(l.strip()) for l in f_]

        with open(self.symbolTablePath) as f_:
            self.symbolTable = dict(line.strip().split() for line in f_)

        self.symbolTableToInt = dict((val, key) for key, val in
                                     self.symbolTable.items())

        with open(self.lexiconTxtPath) as f_:
            # self.lexicon = {}
            # for line in f_:
            #     try:
            #         self.lexicon[line.strip().split('\t')[0]] = line.strip().split('\t')[1].split(' ')
            #     except IndexError as e:
            #         print(line)
            self.lexicon = {line.strip().split('\t')[0]:line.strip().split('\t')[1].split(' ')
                            for line in f_}

        self.avgPhonemeCount = round(sum([len(key) for val, key in self.lexicon.items()]) / max(len(self.lexicon), 1)) # thanks, NPE, http://stackoverflow.com/a/7716358/5272567

        try:
            #: Absolute path to Kaldi top-level dir
            self.kaldiRoot = os.environ['KALDI_ROOT']
        except KeyError:
            self.kaldiRoot = _DEFAULT_KALDI_ROOT

    @classmethod
    def _validateModel(cls, modelPath, graphs=True):
        missingFiles = []
        if not os.path.isdir(modelPath):
            raise MarosijoError(
                'The supplied modelPath "{}" either does not exist or is not a directory'
                .format(modelPath))

        if graphs:
            requiredFiles = cls._REQUIRED_FILES + cls._REQUIRED_FILES_AFTER_COMPILE
            extraMsg = 'Did you forget to run the graph generation script?'
        else:
            requiredFiles = cls._REQUIRED_FILES
            extraMsg = 'Did you forget the model preparation step?'

        for file_ in requiredFiles:
            fileExists = os.path.exists(os.path.join(modelPath, file_))
            if not fileExists:
                missingFiles.append(file_)

        if missingFiles:
            raise MarosijoError('Following model files are missing from "{}": {}.  {}'
                                .format(modelPath, ', '.join(f_ for f_ in missingFiles),
                                        extraMsg))

    def symToInt(self, token: str, forceLowercase=True) -> str:
        def lower(s, lower=True):
            return s.lower() if lower else s

        return ' '.join(self.symbolTable.get(token_, str(self.oov)) for
                        token_ in lower(token, lower=forceLowercase).split())

    def intToSym(self, tokenInts: str, fromCol=0, toCol=None) -> str:
        return ' '.join(self.symbolTableToInt[token_] for token_ in
                        tokenInts.split()[fromCol:toCol])

class _SimpleMarosijoTask(Task):
    """_SimpleMarosijoTask
    ===============

    QC module/base task which uses custom decoding graphs, based on
    ideas from [1], and a monophone speech recognizer trained on a
    small (a few hrs) dataset of in-domain data. The results for each
    recording/utterance are a binary value, representing whether it is
    deemed valid or not. The findings are stored as a report in the
    redis datastore under the keys 'report/SimpleMarosijoTask'

    [1] Panayotov, V., Chen, G., Povey, D., & Khudanpur, S. (2015). Librispeech: An ASR corpus based on public domain audio books. In ICASSP, IEEE International Conference on Acoustics, Speech and Signal Processing - Proceedings (Vol. 2015-August, pp. 5206–5210). http://doi.org/10.1109/ICASSP.2015.7178964

    """

    abstract = True

    @property
    def redis(self):
        if not hasattr(self, '_redis'):
            self._redis = redis.StrictRedis(
                host=celery_config.const['host'],
                port=celery_config.const['port'],
                db=celery_config.const['backend_db'])
        return self._redis

    @property
    def common(self):
        """Data common to MarosijoModule and MarosijoGenGraphs

        """
        if not hasattr(self, '_common'):
            self._common = MarosijoCommon(downsample=True)
        return self._common

    @property
    def decodedScpRefs(self):
        """
        Returns the reference part of graphs.scp contents in memory as a dict. Indexed
        by the tokenId.

        {'tokenId' -> 'reference in .ark file (corresponding to the data in a .scp file) '}
        so we can take from this the lines we need to form the partial
        .scp to pass into Kaldi scripts

        """
        if not hasattr(self, '_decodedScpRefs'):
            self._decodedScpRefs = dict()
            with open(self.common.graphsScpPath) as f:
                for line in f:
                    line = line.strip()
                    tokenKey = line.split()[0]
                    arkRef = line.split(' ')[1:]
                    self._decodedScpRefs[tokenKey] = ' '.join(arkRef)

        return self._decodedScpRefs

    def processBatch(self, name, session_id, indices) -> bool:
        """
        The main processing function of this module. This function
        is called to do processing on a batch of recordings from the session.

        Parameters:

            name        the name to use to write the report to redis datastore
                        at 'report/name/session_id'
            session_id  id of session
            indices     indices in the list of recordings in the redis
                        datastore ('session/session_id/recordings') to process
                        in this batch.

        Return:
            False or raise an exception if something is wrong (and
            this should not be called again.)
        """
        if not indices:
            # Nothing left to process.
            return True

        #: Set up commands
        computeMfccFeats = sh.Command('{}/src/featbin/compute-mfcc-feats'
                                      .format(self.common.kaldiRoot))
        computeMfccFeats = computeMfccFeats.bake(
            '--sample-frequency={}'.format(self.common.sampleFreq),
            '--use-energy=false',
            '--snip-edges=false')
        gmmLatgenFaster = sh.Command('{}/src/gmmbin/gmm-latgen-faster'
                                     .format(self.common.kaldiRoot))
        latticeBestPath = sh.Command('{}/src/latbin/lattice-best-path'
                                      .format(self.common.kaldiRoot))

        recordings = json.loads(
            self.redis.get(
                'session/{}/recordings'.format(session_id)).decode('utf-8'))

        recordings = [rec for i, rec in  enumerate(recordings) if i in indices]

        with tempfile.TemporaryDirectory(prefix='qc') as tmpdir:
            tokensGraphsScpPath = os.path.join(tmpdir, 'graphs.scp')
            mfccFeatsScpPath = os.path.join(tmpdir, 'feats.scp')
            mfccFeatsPath = os.path.join(tmpdir, 'feats.ark')
            tokensPath = os.path.join(tmpdir, 'tokens')
            editsPath = os.path.join(tmpdir, 'edits')  # ???
            with open(tokensPath, 'w') as tokensF, \
                 open(mfccFeatsScpPath, 'w') as mfccFeatsTmp, \
                 open(tokensGraphsScpPath, 'w') as tokensGraphsScp:

                graphsScp = []
                for r in recordings:
                    if self.common.downsample:
                        print('{rec_id} sox {rec_path} -r{sample_freq} -t wav - |'
                              .format(
                                  rec_id=r['recId'],
                                  rec_path=r['recPath'],
                                  sample_freq=self.common.sampleFreq), file=mfccFeatsTmp)
                    else:
                        print('{} {}'.format(r['recId'], r['recPath']),
                              file=mfccFeatsTmp)

                    tokenInts = self.common.symToInt(r['token'])

                    print('{} {}'.format(r['recId'], tokenInts),
                          file=tokensF)

                    try:
                        graphsScp.append('{} {}'.format(r['recId'],
                                                        self.decodedScpRefs[str(r['tokenId'])]))
                    except KeyError as e:
                        log('Error, probably could not find key in MarosijoModule/local/graphs.scp, id: {}, prompt: {}'
                             .format(r['tokenId'], r['token']))
                        raise

                # make sure .scp file is sorted on keys
                graphsScp = sorted(graphsScp, key=lambda x: x.split()[0])
                for line in graphsScp:
                    print(line, file=tokensGraphsScp)

            try:
                # We save the features on disk (the ,p means permissive. Let kaldi ignore errors,
                # and handle missing recordings later)
                computeMfccFeats(
                    'scp,p:{}'.format(mfccFeatsScpPath),
                    'ark:{}'.format(mfccFeatsPath))

                computeCmvnCmd = ('{kaldi_root}/src/featbin/compute-cmvn-stats ' +
                                  'ark,p:{mfcc_feats_path} ' +
                                  'ark:- ').format(mfcc_feats_path=mfccFeatsPath,
                                                   kaldi_root=self.common.kaldiRoot)
                featsCmd = ('{kaldi_root}/src/featbin/apply-cmvn ' +
                            '"ark,p:{compute_cmvn_cmd} |" ' +
                            'ark:{mfcc_feats_path} ' +
                            '"ark:| {kaldi_root}/src/featbin/add-deltas ark,p:- ark:-" '
                           ).format(compute_cmvn_cmd=computeCmvnCmd,
                                    mfcc_feats_path=mfccFeatsPath,
                                    kaldi_root=self.common.kaldiRoot)                

                # create a pipe using sh, output of gmm_latgen_faster piped into lattice_oracle
                # piping in contents of tokens_graphs_scp_path and writing to edits_path
                # note: be careful, as of date sh seems to swallow exceptions in the inner pipe
                #   https://github.com/amoffat/sh/issues/309
                # ...
                hypLines = latticeBestPath(
                    gmmLatgenFaster(
                        '--acoustic-scale=0.1',
                        '--beam=12',
                        '--max-active=1000',
                        '--lattice-beam=10.0',
                        '--max-mem=50000000',
                        self.common.acousticModelPath,
                        'scp,p:{}'.format(tokensGraphsScpPath),  # fsts-rspecifier
                        'ark,p:{} |'.format(featsCmd),           # features-rspecifier
                        'ark:-',                                 # lattice-wspecifier
                        _err=errLog,
                        _piped=True),
                    '--acoustic-scale=0.06',
                    '--word-symbol-table={}'.format(self.common.symbolTablePath),
                    'ark,p:-',
                    'ark,t:-',
                    _iter=True,
                    _err=errLog
                )
            except sh.ErrorReturnCode_1 as e:
                # No data (e.g. all wavs unreadable)
                hypLines = []
                log('e.stderr: ', e.stderr)

            def splitAlsoEmpty(s):
                cols = s.split(maxsplit=1)
                if len(cols) == 1:
                    return cols[0], ''
                elif len(cols) == 2:
                    return cols[0], cols[1]
                else:
                    raise ValueError('Unexpected')

            hyps = {str(recId): tok_ for recId, tok_ in
                    (splitAlsoEmpty(line.strip()) for line in hypLines)}

            refs = {str(recId): tok_ for recId, tok_ in
                    ((r['recId'], self.common.symToInt(r['token']))
                     for r in recordings)}

            details = {hypKey: MarosijoAnalyzer(hypTok.split(), refs[hypKey].split(), self.common).details() for
                       hypKey, hypTok in hyps.items()}
            # 'empty' analysis in case Kaldi couldn't analyse recording for some reason
            # look at MarosijoAnalyzer.details() for format
            placeholderDetails = {
                'hybrid': 0.0,
                'phone_acc': 0.0,
                'wer': 0.0,
                'onlyInsOrSub': False,
                'correct': 0,
                'sub': 0,
                'ins': 0,
                'del': 0,
                'startdel': 0,
                'enddel': 0,
                'extraInsertions': 0,
                'empty': False,
                'distance': 0
            }

            edits = {hypKey: details[hypKey]['distance'] for
                     hypKey, hypTok in hyps.items()}

            qcReport = {"sessionId": session_id,
                        "requestId": str(uuid.uuid4()), # just use a uuid
                        "totalStats": {"accuracy": 0.0},
                        "perRecordingStats": []}

            cumAccuracy = 0.0
            for r in recordings:
                error = ''
                try:
                    # this is the old wer where a single phoneme is treated as a single word
                    old_wer = edits[str(r['recId'])] / len(r['token'].split())
                except KeyError as e:
                    # Kaldi must have choked on this recording for some reason
                    if isWavHeaderOnly(r['recPath']):
                        error = 'wav_header_only'
                        log('Error, only wav header in recording: {} for session: {}; {}'
                            .format(r['recId'], session_id, repr(e)))
                    else:
                        # unknown error
                        error = 'unknown_error'
                        log('Error, unknown error processing recording: {} for session {}; {}'
                            .format(r['recId'], session_id, repr(e)))

                try:
                    hyp =  ' '.join([self.common.symbolTableToInt[x] 
                                        for x in hyps[str(r['recId'])].split(' ')]) # hypothesis (words not ints)
                except KeyError as e:
                    if hyps[str(r['recId'])] == '':
                        hyp = ''
                    else:
                        if not error:
                            error = 'hyp_error'
                            log('Error, hypothesis error processing recording: {} for session {}; {}'
                                .format(r['recId'], session_id, repr(e)))

                if not error:
                    old_wer_norm = 0.0 if 1 - old_wer < 0 else 1 - old_wer
                else:
                    old_wer_norm = 0.0
                    hyp = ''

                prec = qcReport['perRecordingStats']
                if not error:
                    analysis = details[str(r['recId'])]
                    analysis.update(error='no_error')
                else:
                    analysis = placeholderDetails
                    analysis.update(error=error)

                analysis.update(old_wer_norm=old_wer_norm)
                analysis.update(hyp=hyp)

                # handle specific errors
                if error == 'wav_header_only':
                    analysis.update(empty=True)

                # use phone accuracy (seemed to give best results)
                accuracy = analysis['phone_acc']

                stats = {"accuracy": accuracy}
                cumAccuracy += accuracy

                stats.update(analysis)
                prec.append({"recordingId": r['recId'], "stats": stats})

            try:
                avgAccuracy = cumAccuracy / len(qcReport['perRecordingStats'])
            except ZeroDivisionError:
                avgAccuracy = 0.0
            else:
                qcReport['totalStats']['accuracy'] = avgAccuracy
                qcReport['totalStats']['avgAcc'] = avgAccuracy

            # If a report exists, we update it.
            # TODO: Do this more efficiently. Need to change how we store reports.
            strReport = self.redis.get('report/{}/{}'.format(name, session_id))
            if strReport:
                oldReport = json.loads(strReport.decode('utf-8'))

                newAvgAccuracy = (oldReport['totalStats']['accuracy'] + qcReport['totalStats']['accuracy']) / 2
                recsDoneThisBatch = len(qcReport['perRecordingStats'])
                newLowerUtt = oldReport['totalStats']['lowerUtt'] + recsDoneThisBatch
                newUpperUtt = oldReport['totalStats']['upperUtt'] + recsDoneThisBatch

                qcReport = update(oldReport, qcReport)

                qcReport['totalStats']['accuracy'] = newAvgAccuracy
                qcReport['totalStats']['lowerUtt'] = newLowerUtt
                qcReport['totalStats']['upperUtt'] = newUpperUtt
            else:
                qcReport['totalStats']['lowerUtt'] = 0
                qcReport['totalStats']['upperUtt'] = len(qcReport['perRecordingStats'])

            self.redis.set('report/{}/{}'.format(name, session_id),
                           json.dumps(qcReport))

        return True


class MarosijoTask(_SimpleMarosijoTask):
    pass
