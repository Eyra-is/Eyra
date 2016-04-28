import os
import json
import tempfile
import sys
import uuid
from functools import partial

import redis
import sh
from celery import Task
import numpy as np

import os.path
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.append(newPath)
import celery_config
from util import errLog
sys.path.remove(newPath)
del newPath


_DEFAULT_KALDI_ROOT = os.path.abspath(
    os.path.join(__file__, '../../../../../../Local/opt/kaldi-trunk'))


class MarosijoError(Exception):
    pass


class MarosijoAnalyzer(object):
    """MarosijoAnalyzer
    ===================

    Does analysis of decoded output, given reference and hypothesis
    string.

    """
    def __init__(self, hypothesis, reference):
        self.reference = reference
        self.hypothesis = hypothesis

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

    def details(self):
        """Returns dict with details of analysis

        """
        res = self.edits()
        seq = self.editSequence()
        details = {'empty': False, 'onlyInsOrSub': False,
                   'enddel': 0, 'startdel': 0, 'extraInsertions': 0}
        details.update(res)
        details.update(ops=seq)

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
                       'sample_freq', 'phone_lm')

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
    def decodedScpLines(self):
        """
        Returns graphs.scp contents in memory as a dict.

        {'tokenId' -> 'corresponding line in .scp script with no newline at the end'}
        so we can take from this the lines we need to form the partial
        .scp to pass into Kaldi scripts

        """
        if not hasattr(self, '_decodedScpLines'):
            self._decodedScpLines = dict()
            with open(self.common.graphsScpPath) as f:
                for line in f:
                    line = line.strip()
                    tokenKey = line.split()[0]
                    self._decodedScpLines[tokenKey] = line

        return self._decodedScpLines

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
                        print('{token_id} sox {rec_path} -r{sample_freq} -t wav - |'
                              .format(
                                  token_id=r['tokenId'],
                                  rec_path=r['recPath'],
                                  sample_freq=self.common.sampleFreq), file=mfccFeatsTmp)
                    else:
                        print('{} {}'.format(r['tokenId'], r['recPath']),
                              file=mfccFeatsTmp)

                    tokenInts = self.common.symToInt(r['token'])

                    print('{} {}'.format(r['tokenId'], tokenInts),
                          file=tokensF)

                    graphsScp.append(self.decodedScpLines[str(r['tokenId'])])

                # make sure .scp file is sorted on keys
                graphsScp = sorted(graphsScp, key=lambda x: x.split()[0])
                for line in graphsScp:
                    print(line, file=tokensGraphsScp)

            # We save the features on disk
            computeMfccFeats(
                'scp:{}'.format(mfccFeatsScpPath),
                'ark:{}'.format(mfccFeatsPath))

            computeCmvnCmd = ('{kaldi_root}/src/featbin/compute-cmvn-stats ' +
                              'ark:{mfcc_feats_path} ' +
                              'ark:- ').format(mfcc_feats_path=mfccFeatsPath,
                                               kaldi_root=self.common.kaldiRoot)
            featsCmd = ('{kaldi_root}/src/featbin/apply-cmvn ' +
                        '"ark:{compute_cmvn_cmd} |" ' +
                        'ark:{mfcc_feats_path} ' +
                        '"ark:| {kaldi_root}/src/featbin/add-deltas ark:- ark:-" '
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
                    'ark:{} |'.format(featsCmd),             # features-rspecifier
                    'ark:-',                                 # lattice-wspecifier
                    _err=errLog,
                    _piped=True),
                '--acoustic-scale=0.06',
                '--word-symbol-table={}'.format(self.common.symbolTablePath),
                'ark:-',
                'ark,t:-',
                _iter=True,
                _err=errLog)

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
                    ((r['tokenId'], self.common.symToInt(r['token']))
                     for r in recordings)}

            details = {hypKey: MarosijoAnalyzer(hypTok.split(), refs[hypKey].split()).details() for
                       hypKey, hypTok in hyps.items()}

            edits = {hypKey: details[hypKey]['distance'] for
                     hypKey, hypTok in hyps.items()}

            qcReport = {"sessionId": session_id,
                        "requestId": str(uuid.uuid4()), # just use a uuid
                        "totalStats": {"accuracy": 0.0},
                        "perRecordingStats": []}

            # TODO: use something other than WER (binary value perhaps)
            cumAccuracy = 0.0
            for r in recordings:
                wer = edits[str(r['tokenId'])] / len(r['token'].split())
                accuracy = 0.0 if 1 - wer < 0 else 1 - wer
                cumAccuracy += accuracy

                prec = qcReport['perRecordingStats']
                stats = {"accuracy": accuracy}
                stats.update(details[str(r['tokenId'])])
                # FIXME: recordingId should be the actual recording ID... (does't really matter though)
                prec.append({"recordingId": r['tokenId'], "stats": stats})

            try:
                avgAccuracy = cumAccuracy / len(qcReport['perRecordingStats'])
            except ZeroDivisionError:
                avgAccuracy = 0.0
            else:
                qcReport['totalStats']['accuracy'] = avgAccuracy

            self.redis.set('report/{}/{}'.format(name, session_id),
                            json.dumps(qcReport))

        return True


class MarosijoTask(_SimpleMarosijoTask):
    pass
