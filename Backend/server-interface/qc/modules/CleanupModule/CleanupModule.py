import redis
import os
import json
import pipes
import tempfile
import sh

from celery import Task

# grab celery_config from 2 dirs above this one
# thanks, Alex Martelli, http://stackoverflow.com/a/1054293/5272567
import sys
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.append(newPath)
import celery_config
sys.path.remove(newPath)
del newPath
# grab errLog from util from 3 dirs above this one
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir))
sys.path.append(newPath)
from util import errLog
sys.path.remove(newPath)
del newPath

class CleanupCommon():
    """
    Variables/files/data common to CleanupTask and CleanupGenGraphs.
    """

    def __init__(self):
        # TODO: use config instead of hardcoded values!

        oldDir = os.getcwd()
        try:
            # change to directory of this file (for using relative paths)
            os.chdir(os.path.dirname(os.path.realpath(__file__)))

            #: Mapping from symbols to integer ids
            self.sym_id_path = 'data/words.syms'
            with open(self.sym_id_path, 'rt') as sf:
                self.sym_id_map = dict(line.strip().split() for line in sf)

            #: Mapping from integer ids to symbols
            self.id_sym_map = dict((val, key) for key, val in self.sym_id_map.items())

            #: Phonetic context decision tree
            self.decision_tree_path = 'data/tri1.tree'

            #: Acoustic model
            self.acoustic_model_path = 'data/tri1.acoustic_mdl'
            with open(self.acoustic_model_path, 'rb') as af:
                self.acoustic_model = af.read()

            #: Integer ID for the out of vocabulary symbol (OOV)
            self.oov_sym = '<UNK>'
            self.oov_id = self.sym_id_map[self.oov_sym]

            #: Lexicon FST with disambiguation symbols, keep it in memory
            self.l_disambig_fst_path = 'data/L_disambig.fst'
            with open(self.l_disambig_fst_path, 'rb') as lf:
                self.l_disambig_fst = lf.read()

            #: List of integer IDs of the disambiguation symbols
            self.disambig_ids_path = 'data/disambig.int'
            with open(self.disambig_ids_path, 'rt') as df:
                self.disambig_ids = df.read().split()

            #:
            self.top_words_path = 'data/top_words.int'
            with open(self.top_words_path, 'rt') as dw:
                self.top_words = [l.strip() for l in dw]

            self.kaldi_root = '../../../../../Local/opt/kaldi-trunk'

            self.sample_freq = 16000
            self.downsample = True
        finally:
            os.chdir(oldDir)


class CleanupTask(Task):
    """CleanupTask -- Module implementing a version of the Kaldi cleanup routines.
    ====================
    
    QC module/base task which takes inspiration from the Kaldi cleanup routines to
    find bad utterances. 
    In short, uses decoding graphs pre-generated for each token (see CleanupGenGraphs.py)
    and then uses a very simple (unigram) speech recognizor on the incoming recorded
    utterances and compares these, and sets a report on it's findings in 
    'report/CleanupModule/session_id'.

    """
    abstract = True
    _common = None
    _decodedScpLines = None
    _redis = None

    decoded_graphs_path = 'local/decoded_graphs.scp'
    # path to root folder of recordings/ folder (or the location of 
    #   the actual .wav recordings) so that rec_folder_path+rel_path
    #   is the correct path to the actual recordings from this files directory
    rec_folder_path = '../../../' 

    @property
    def common(self):
        """ Variables common to CleanupModule and CleanupGenGraphs
        """
        if self._common is None:
            self._common = CleanupCommon()
        return self._common

    @property
    def decodedScpLines(self):
        """
        Keep our decoded_graphs.scp file in memory as a dict
        {'tokenId' -> 'corresponding line in .scp script with no newline at the end'}
        so we can take from this the lines we need to form the partial
        .scp to pass into Kaldi scripts
        """
        if self._decodedScpLines is None:
            self._decodedScpLines = {}
            oldDir = os.getcwd()
            try:
                # change to directory of this file (for using relative paths)
                os.chdir(os.path.dirname(os.path.realpath(__file__)))

                with open(self.decoded_graphs_path) as f:
                    for line in f.read().splitlines():
                        tokId = line.split()[0]
                        self._decodedScpLines[tokId] = line
            finally:
                # restore old cwd
                os.chdir(oldDir)
        return self._decodedScpLines

    @property
    def redis(self):
        """ Connection to redis datastore.
        """
        if self._redis is None:
            self._redis = redis.StrictRedis(
                host=celery_config.const['host'], 
                port=celery_config.const['port'], 
                db=celery_config.const['backend_db'])
        return self._redis

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

        if indices == []:
            return True

        beam = 15.0
        max_active = 750
        lattice_beam = 8.0
        acoustic_scale = 0.1

        oldDir = os.getcwd()
        try:
            # change to directory of this file (for using relative paths)
            os.chdir(os.path.dirname(os.path.realpath(__file__)))

            # set up commands for sh
            compute_mfcc_feats = sh.Command('{}/src/featbin/compute-mfcc-feats'
                                            .format(self.common.kaldi_root))
            gmm_latgen_faster = sh.Command('{}/src/gmmbin/gmm-latgen-faster'
                                            .format(self.common.kaldi_root))
            lattice_oracle = sh.Command('{}/src/latbin/lattice-oracle'
                                        .format(self.common.kaldi_root))

            # grab the recordings list for this session
            recordings = json.loads(self.redis.get('session/{}/recordings'.format(session_id)).decode('utf8'))
            # only use recordings[indices] as per our batch
            recordings = [rec for i,rec in enumerate(recordings) if i in indices]

            # make a new temp .scp file which will signify a .scp file only for our tokens
            #   in these recordings
            _, tokens_graphs_scp_path = tempfile.mkstemp(prefix='qc')
            # other tempfiles
            _, mfcc_feats_scp_path = tempfile.mkstemp(prefix='qc')
            _, mfcc_feats_path = tempfile.mkstemp(prefix='qc')
            _, tokens_path = tempfile.mkstemp(prefix='qc')
            _, edits_path = tempfile.mkstemp(prefix='qc')
            with open(tokens_path, 'wt') as tokens_f, \
                    open(mfcc_feats_scp_path, 'w') as mfcc_feats_tmp, \
                    open(tokens_graphs_scp_path, 'w') as tokens_graphs_scp:

                graphs_scp = [] # will contain list of lines in scp script referencing relevant decoded graphs
                for r in recordings:
                    if self.common.downsample:
                        print('{token_id} sox {rec_path} -r{sample_freq} -t wav - |'.format(token_id=r['tokenId'],
                                                                                            rec_path=self.rec_folder_path+r['recPath'],
                                                                                            sample_freq=self.common.sample_freq),
                              file=mfcc_feats_tmp)
                    else:
                        print('{} {}'.format(r['tokenId'], r['recPath']),
                              file=mfcc_feats_tmp)

                    token_ids = ' '.join(self.common.sym_id_map.get(tok, self.common.oov_id) for
                                         tok in r['token'].split())
                    print('{} {}'.format(r['tokenId'], token_ids),
                          file=tokens_f)

                    graphs_scp.append(self.decodedScpLines[str(r['tokenId'])])

                # make sure .scp file is sorted on keys
                graphs_scp = sorted(graphs_scp, key=lambda x: x.split()[0])
                for line in graphs_scp:
                    print(line, file=tokens_graphs_scp)

            # MFCCs are needed at 2 stages of the pipeline so we have to dump on disk
            compute_mfcc_feats(
                '--sample-frequency={}'.format(self.common.sample_freq),
                '--use-energy=false',
                'scp:{}'.format(mfcc_feats_scp_path),
                'ark:{}'.format(mfcc_feats_path)
            )

            compute_cmvn_cmd = ('{kaldi_root}/src/featbin/compute-cmvn-stats ' +
                                '"ark:{mfcc_feats_path}" ' +
                                '"ark:-" ').format(mfcc_feats_path=mfcc_feats_path,
                                                   kaldi_root=self.common.kaldi_root)
            feats_cmd = ('{kaldi_root}/src/featbin/apply-cmvn ' +
                         '"ark:{compute_cmvn_cmd} |" ' +
                         '"ark:{mfcc_feats_path}" ' +
                         '"ark:| {kaldi_root}/src/featbin/add-deltas ark:- ark:-" '
                        ).format(compute_cmvn_cmd=compute_cmvn_cmd,
                                 mfcc_feats_path=mfcc_feats_path,
                                 kaldi_root=self.common.kaldi_root)

            # create a pipe using sh, output of gmm_latgen_faster piped into lattice_oracle
            # piping in contents of tokens_graphs_scp_path and writing to edits_path
            # note: be careful, as of date sh seems to swallow exceptions in the inner pipe
            #   https://github.com/amoffat/sh/issues/309
            lattice_oracle( 
                gmm_latgen_faster(
                    sh.cat(
                        tokens_graphs_scp_path,
                        _piped=True,
                        _err=errLog
                    ),
                    '--acoustic-scale={}'.format(acoustic_scale),
                    '--beam={}'.format(beam),
                    '--max-active={}'.format(max_active),
                    '--lattice-beam={}'.format(lattice_beam),
                    '--word-symbol-table={}'.format(self.common.sym_id_path),
                    '{}'.format(self.common.acoustic_model_path),
                    'scp:-',
                    'ark:{} |'.format(feats_cmd),
                    'ark:-',
                    _piped=True,
                    _err=errLog
                ),
                'ark:-', 
                'ark:{ref_tokens}'.format(ref_tokens=tokens_path), 
                'ark:/dev/null', 
                'ark,t:-',
                _out=edits_path
            )

            with open(edits_path, 'rt') as edits_f:
                edits = dict((int(rec_id), int(n_edits)) for rec_id, n_edits
                             in (line.strip().split() for line in edits_f))
        finally:
            os.chdir(oldDir)

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
            wer = edits[r['tokenId']] / len(r['token'].split())
            accuracy = 0.0 if 1 - wer < 0 else 1 - wer
            cum_accuracy += accuracy

            prec = qc_report['perRecordingStats']
            stats = {"accuracy": accuracy}
            prec.append({"recordingId": r['tokenId'], "stats": stats})

        try:
            avg_accuracy = cum_accuracy / len(qc_report['perRecordingStats'])
        except ZeroDivisionError:
            avg_accuracy = 0.0
        else:
            qc_report['totalStats']['accuracy'] = avg_accuracy

        self.redis.set('report/{}/{}'.format(name, session_id), 
                        qc_report)

        return True
