import json
from io import StringIO, BytesIO
import tempfile # mkfifo...
import pipes
import importlib
import os

import sh
import redis

#: Relative imports
from util import log
from celery_handler import CeleryHandler

class QcError(Exception):
    """QcError
    ==========

    Trouble in paradise. Raised if QC experienced a critical error.

    """
    pass


class _QcHandler(object):
    """QcHandler
    ============

    Encapsulates quality control reporting

    """
    def __init__(self, app):
        # TODO: use app config instead of hardcoded values!

        #: Mapping from symbols to integer ids
        self.sym_id_path = 'qcdata/words.syms'
        with open(self.sym_id_path, 'rt') as sf:
            self.sym_id_map = dict(line.strip().split() for line in sf)

        #: Mapping from integer ids to symbols
        self.id_sym_map = dict((val, key) for key, val in self.sym_id_map.items())

        #: Phonetic context decision tree
        self.decision_tree_path = 'qcdata/tri1.tree'

        #: Acoustic model
        self.acoustic_model_path = 'qcdata/tri1.acoustic_mdl'
        with open(self.acoustic_model_path, 'rb') as af:
            self.acoustic_model = af.read()

        #: Integer ID for the out of vocabulary symbol (OOV)
        self.oov_sym = '<UNK>'
        self.oov_id = self.sym_id_map[self.oov_sym]

        #: Lexicon FST with disambiguation symbols, keep it in memory
        self.l_disambig_fst_path = 'qcdata/L_disambig.fst'
        with open(self.l_disambig_fst_path, 'rb') as lf:
            self.l_disambig_fst = lf.read()

        #: List of integer IDs of the disambiguation symbols
        self.disambig_ids_path = 'qcdata/disambig.int'
        with open(self.disambig_ids_path, 'rt') as df:
            self.disambig_ids = df.read().split()

        #:
        self.top_words_path = 'qcdata/top_words.int'
        with open(self.top_words_path, 'rt') as dw:
            self.top_words = [l.strip() for l in dw]

        self.kaldi_root = '../../Local/opt/kaldi-trunk'

        self.sample_freq = 16000
        self.downsample = True

    def getReport(self, session_id, recordings: list) -> dict:
        """Return a quality report for the batch of recordings listed in `recordings`

        Parameters:

          session_id   ...
          recordings   [{"recId": ..., "token": str, "recPath": str}]

        Returns:

        {"sessionId": ...,
         "requestId": ...,
         "totalStats": {"accuracy": ..."},
         "perRecordingStats": [{"recordingId": ...,
                                "stats": {"accuracy": ...},
         }]}

        """
        # TODO: make efficient
        scale_opts = '--transition-scale=1.0 --self-loop-scale=0.1'
        beam = 15.0
        max_active = 750
        lattice_beam = 8.0
        acoustic_scale = 0.1

        # MFCCs are needed at 2 stages of the pipeline so we have to dump on disk
        mfcc_pipe = pipes.Template()
        compute_mfcc_cmd = ('{kaldi_root}/src/featbin/compute-mfcc-feats ' +
                           '--sample-frequency={sample_freq} --use-energy=false ' +
                            'scp:- ark:- ').format(kaldi_root=self.kaldi_root,
                                                   sample_freq=self.sample_freq)
        mfcc_pipe.append(compute_mfcc_cmd, '--')

        # TODO: try to eliminate the use of tempfiles
        _, mfcc_feats_path = tempfile.mkstemp(prefix='qc')
        _, tokens_path = tempfile.mkstemp(prefix='qc')
        _, edits_path = tempfile.mkstemp(prefix='qc')
        with open(tokens_path, 'wt') as tokens_f, \
             mfcc_pipe.open(mfcc_feats_path, 'w') as mfcc_feats_tmp:
            for r in recordings:
                if self.downsample:
                    print('{rec_id} sox {rec_path} -r{sample_freq} -t wav - |'.format(rec_id=r['recId'],
                                                                                      rec_path=r['recPath'],
                                                                                      sample_freq=self.sample_freq),
                          file=mfcc_feats_tmp)
                else:
                    print('{} {}'.format(r['recId'], r['recPath']),
                          file=mfcc_feats_tmp)
                token_ids = ' '.join(self.sym_id_map.get(tok, self.oov_id) for
                                     tok in r['token'].split())
                print('{} {}'.format(r['recId'], token_ids),
                      file=tokens_f)

        compute_cmvn_cmd = ('{kaldi_root}/src/featbin/compute-cmvn-stats ' +
                            '"ark:{mfcc_feats_path}" ' +
                            '"ark:-" ').format(mfcc_feats_path=mfcc_feats_path,
                                               kaldi_root=self.kaldi_root)
        feats_cmd = ('{kaldi_root}/src/featbin/apply-cmvn ' +
                     '"ark:{compute_cmvn_cmd} |" ' +
                     '"ark:{mfcc_feats_path}" ' +
                     '"ark:| {kaldi_root}/src/featbin/add-deltas ark:- ark:-" '
                    ).format(compute_cmvn_cmd=compute_cmvn_cmd,
                             mfcc_feats_path=mfcc_feats_path,
                             kaldi_root=self.kaldi_root)

        safer_pipeline = pipes.Template()
        safer_pipeline.append('./make_utterance_fsts.pl {top_words}'
                              .format(top_words=self.top_words_path), '--')
        safer_pipeline.append(('{kaldi_root}/src/bin/compile-train-graphs-fsts ' +
                               '{scale_opts} ' +
                               '--read-disambig-syms={disambig_ids} ' +
                               '{tree} ' +
                               '{acoustic_model} ' +
                               '{l_disambig_fst} ' +
                               'ark:- ark:-').format(scale_opts=scale_opts,
                                                     disambig_ids=self.disambig_ids_path,
                                                     tree=self.decision_tree_path,
                                                     acoustic_model=self.acoustic_model_path,
                                                     l_disambig_fst=self.l_disambig_fst_path,
                                                     kaldi_root=self.kaldi_root),
                              '--')

        safer_pipeline.append(('{kaldi_root}/src/gmmbin/gmm-latgen-faster ' +
                               '--acoustic-scale={acoustic_scale} ' +
                               '--beam={beam} ' +
                               '--max-active={max_active} ' +
                               '--lattice-beam={lattice_beam} ' +
                               '--word-symbol-table={sym_id_path} ' +
                               '{acoustic_model} ' +
                               'ark:- ' +
                               '"ark:{feats} |" ' +
                               'ark:- ').format(kaldi_root=self.kaldi_root,
                                                acoustic_scale=acoustic_scale, beam=beam,
                                                max_active=max_active, lattice_beam=lattice_beam,
                                                sym_id_path=self.sym_id_path,
                                                acoustic_model=self.acoustic_model_path,
                                                feats=feats_cmd.replace('"', r'\"')),
                              '--')
        safer_pipeline.append(('{kaldi_root}/src/latbin/lattice-oracle ' +
                               'ark:- ' +
                               '"ark:{ref_tokens}" ' +
                               'ark:/dev/null ' + # we don't need the actual hypothesis
                               ' "ark,t:-" '      # number of edits
                               )
                              .format(kaldi_root=self.kaldi_root, ref_tokens=tokens_path), '--')

        # Run the tokens through the decoding/scoring pipeline
        safer_pipeline.copy(tokens_path, edits_path)

        with open(edits_path, 'rt') as edits_f:
            edits = dict((int(rec_id), int(n_edits)) for rec_id, n_edits
                         in (line.strip().split() for line in edits_f))

        # We should return something like this
        # {"sessionId": ...,
        # "requestId": ...,
        # "totalStats": {"accuracy": [0.0;1.0]"},
        # "perRecordingStats": [{"recordingId": ...,
        #                        "stats": {"accuracy": [0.0;1.0]},
        #                         }]}
        qc_report = {"sessionId": session_id,
                     "requestId": -1, # maybe just use a uuid?
                     "totalStats": {"accuracy": 0.0},
                     "perRecordingStats": []}

        cum_accuracy = 0.0
        for r in recordings:
            wer = edits[int(r['recId'])] / len(r['token'].split())
            accuracy = 0.0 if 1 - wer < 0 else 1 - wer
            cum_accuracy += accuracy

            prec = qc_report['perRecordingStats']
            stats = {"accuracy": accuracy}
            prec.append({"recordingId": r['recId'], "stats": stats})

        try:
            avg_accuracy = cum_accuracy / len(qc_report['perRecordingStats'])
        except ZeroDivisionError:
            avg_accuracy = 0.0
        else:
            qc_report['totalStats']['accuracy'] = avg_accuracy

        return qc_report

class DummyHandler(object):
    """DummyHandler - Do no quality control
    ===============

    A call to DummyHandler.getReport always returns:

        {'sessionId': ..., 'status': 'inactive'}

    """
    def __init__(self, app):
        """Initialise a DummyHandler for QC handling"""
        self.app = app

    def getReport(self, session_id):
        return {"sessionId": session_id, "status": "inactive"}


#####################
#: AsyncCleanHandler

#from tasks import qc_clean_process

class AsyncCleanHandler(object):
    """AsyncCleanHandler -- Asynchronous QC handler based on ...
    ====================
    # TODO: reference properly

    Async handler using Celery workers for computation and Redis for
    temporary data.

    A few important app.config options:

      ASYNC_CLEAN_HANDLER_MODEL_PATH    path to the trained "model"
      ASYNC_CLEAN_HANDLER_BATCH_SIZE    max number of recordings to analyse
                                        per task

    """
    def __init__(self, app, model_path='./qcdata', batch_size=5):
        """Initialise an AsyncCleanHandler

        """
        self.model_path = app.config.get('ASYNC_CLEAN_HANDLER_MODEL_PATH', None)
        if self.model_path is None:
            self.model_path = model_path
        self._load_model(model_path)
        # TODO: use these variables as configs
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

        self.celeryHandler = CeleryHandler(app)

    def _load_model(self, model_path):
        # TODO: define "model format"; Just a zip file with the necessary files?
        #: Mapping from symbols to integer ids
        self.sym_id_path = os.path.join(model_path, 'words.syms')
        with open(self.sym_id_path, 'rt') as sf:
            self.sym_id_map = dict(line.strip().split() for line in sf)

        #: Mapping from integer ids to symbols
        self.id_sym_map = dict((val, key) for key, val in self.sym_id_map.items())

        #: Phonetic context decision tree
        self.decision_tree_path = os.path.join(model_path, 'tri1.tree')

        #: Acoustic model
        self.acoustic_model_path = os.path.join(model_path, 'tri1.acoustic_mdl')
        with open(self.acoustic_model_path, 'rb') as af:
            self.acoustic_model = af.read()

        #: Integer ID for the out of vocabulary symbol (OOV)
        self.oov_sym = '<UNK>'
        self.oov_id = self.sym_id_map[self.oov_sym]

        #: Lexicon FST with disambiguation symbols, keep it in memory
        self.l_disambig_fst_path = os.path.join(model_path, 'L_disambig.fst')
        with open(self.l_disambig_fst_path, 'rb') as lf:
            self.l_disambig_fst = lf.read()

        #: List of integer IDs of the disambiguation symbols
        self.disambig_ids_path = os.path.join(model_path, 'disambig.int')
        with open(self.disambig_ids_path, 'rt') as df:
            self.disambig_ids = df.read().split()

        #: Popular words. Fillers?
        self.top_words_path = os.path.join(model_path, 'top_words.int')
        with open(self.top_words_path, 'rt') as dw:
            self.top_words = [l.strip() for l in dw]

        self.kaldi_root = '../../Local/opt/kaldi-trunk'

        self.sample_freq = 16000
        self.downsample = True

    def getReport(self, session_id: int) -> dict:
        """Returns a QC report

        If session with ``session_id`` exists:
          If in datastore: Read from datastore and return
          Otherwise: Return started message and start the task if not started

        Otherwise: Return raise/signal an error

        """

        # TODO: check if session exists
        report = self.redis.get('report/{}'.format(session_id))
        if report is not None:
            return report\
                    .decode("utf-8") # redis.get returns bytes, so we decode into string
        else:
            self.celeryHandler.qcProcessSession(session_id, 0)
            return dict(sessionId=session_id, status='started')


class QcHandler(object):
    """QcHandler
    ============

    Proxy class for handling quality control reporting.

    Its only public method is :meth:`getReport`. See its docstring for
    details.

    Use the handler class in app.config['QC_HANDLER_CLASS'] if it
    exists, otherwise ``processing_cls`` is used (which defaults to
    ``.qc_handler.DummyHandler``)

    Usage:

    >>> qc = QcHandler(app)
    >>> qc.getReport(1)
    {'sessionId': 1, 'status': 'started'}
    ... wait ...
    >>> qc.getReport(1)
    {"sessionId": 1,
     "status": "processing",
     "totalStats": {"accuracy": [0.0;1.0]"},
     "perRecordingStats": [{"recordingId": ...,
                            "stats": {"accuracy": [0.0;1.0]}}]}

    """

    def __init__(self, app, processing_cls=DummyHandler):
        """Initialise a QC handler

        app.config['QC_HANDLER_CLASS'] should be a fqn of a QC
        handling class, i.e. a class that implements the getReport
        method. If it's not set ``processing_cls`` is used instead.

        """
        handler_name = app.config.get('QC_HANDLER_CLASS', None)
        if handler_name is not None:
            try:
                importlib.import_module(handler_name)
                self.handler = handler(app)
            except ImportError as exc:
                log("Unable to import QC handler from config: QC_HANDLER_CLASS='{}'"
                    .format(handler_name), e=exc)
                raise
        else:
            self.handler = processing_cls(app)

    def getReport(self, session_id) -> dict:
        """Return a quality report for the session ``session_id``, if
        available otherwise we start a background task to process
        currently available recordings.

        Parameters:

          session_id   ...
          recordings   [{"recId": ..., "token": str, "recPath": str}]

        Returned dict if the QC report is not available, but is being
        processed:

            {"sessionId": ...,
             "status": "started"}

        Returned dict definition if no QC module is active:

            {"sessionId": ...,
             "status": "inactive"}

        Returned dict definition:

            {"sessionId": ...,
             "status": "processing",
             "totalStats": {"accuracy": [0.0;1.0]"},
             "perRecordingStats": [{"recordingId": ...,
                                    "stats": {"accuracy": [0.0;1.0]},
                                    ... TBD ...}]
            }

        """
        return self.handler.getReport(session_id)
