import json
from io import StringIO, BytesIO
import tempfile
import pipes

from util import log

class QcHandler(object):
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
            wer = edits[r['recId']] / len(r['token'].split())
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
