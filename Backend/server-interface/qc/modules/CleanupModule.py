import redis
import os

# grab celery_config from dir above this one
# thanks, Alex Martelli, http://stackoverflow.com/a/1054293/5272567
import sys
import os.path
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(newPath)
import celery_config
sys.path.remove(newPath)
del newPath

from celery import Task

class CleanupCommon():
    """
    Variables/files/data common to CleanupTask and CleanupGenGraphs.
    """

    def __init__(self):
        # TODO: use config instead of hardcoded values!

        oldDir = os.getcwd()
        try:
            # change to directory of this file (for using relative paths like data/*)
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

            self.kaldi_root = '../../../../Local/opt/kaldi-trunk'

            self.sample_freq = 16000
            self.downsample = True
        finally:
            # restore old cwd
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
    _redis = None
    _common = None

    @property
    def redis(self):
        if self._redis is None:
            self._redis = redis.StrictRedis(
                host=celery_config.const['host'], 
                port=celery_config.const['port'], 
                db=celery_config.const['backend_db'])
        return self._redis

    @property
    def common(self):
        """ Variables common to CleanupModule and CleanupGenGraphs
        """
        if self._common is None:
            self._common = CleanupCommon()
        return self._common

    def processBatch(self, name, session_id, indices) -> bool:
        """
        The main processing function of this module. This function 
        is called to do processing on a batch of recordings from the session.

        Parameters:

            name        the name to use to write the report to redis datastore
                        at 'report/name/session_id'
            session_id  id of session
            indices     indices in the list of recordings in the redis 
                        datastore ('session/session_id/recordings')

        Return:
            False or raise an exception if something is wrong (and
            this should not be called again.)
        """

        beam = 15.0
        max_active = 750
        lattice_beam = 8.0
        acoustic_scale = 0.1
        
        # self.common

        print('In CLEANUP processing batch, indices: {}'.format(indices))
        self.redis.set('report/{}/{}'.format(name, session_id), 
                        {'report':'A CLEANUP REPORT, indices: {}'.format(indices)})
        return True
