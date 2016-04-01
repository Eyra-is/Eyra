import sh
import tempfile
import pipes

from CleanupModule import CleanupCommon
from util import DbWork

def genGraphs():
    """
    Generate decoding graphs for each token for our Cleanup module.
    """

    decoded_ark_path = 'decoded_graph.ark'
    decoded_scp_path = 'decoded_graph.scp'
    tokens_path = 'token_test.txt'#'../../../db/src/mim_malr_tokens_plus_rare.txt'

    # init constants and open files
    common = CleanupCommon()

    # TODO: make efficient
    scale_opts = '--transition-scale=1.0 --self-loop-scale=0.1'

    #: Mapping from symbols to integer ids
    sym_id_path = 'data/words.syms'
    with open(sym_id_path, 'rt') as sf:
        sym_id_map = dict(line.strip().split() for line in sf)

    #: Mapping from integer ids to symbols
    id_sym_map = dict((val, key) for key, val in sym_id_map.items())

    # TODO: try to eliminate the use of tempfiles (mkfifo)
    _, tokens_w_key_path = tempfile.mkstemp(prefix='qc')
    with open(tokens_path, 'r') as tokens_f, \
            open(tokens_w_key_path, 'wt') as tokens_with_id_f:
        # mysql starts counting at 1. These tok_keys should correspond to mysql id's
        #   of tokens (because this is crucial, since the cleanup module relies
        #   on the ids, we make sure to verify this by querying the database for each token
        #   see util.DbWork)
        dbWork = DbWork()
        tok_key = 1 
        for token in tokens_f.read().splitlines():
            token_ids = ' '.join(common.sym_id_map.get(tok, common.oov_id) for
                                 tok in token.split())
            if dbWork.verifyTokenId(tok_key, token):
                print('{} {}'.format(tok_key, token_ids),
                      file=tokens_with_id_f)
            else:
                raise ValueError('Token not verified, %s with id %d.' % (token, tok_key))
            tok_key += 1

    safer_pipeline = pipes.Template()
    safer_pipeline.append('./make_utterance_fsts.pl {top_words}'
                          .format(top_words=common.top_words_path), '--')
    safer_pipeline.append(('{kaldi_root}/src/bin/compile-train-graphs-fsts ' +
                           '{scale_opts} ' +
                           '--read-disambig-syms={disambig_ids} ' +
                           '{tree} ' +
                           '{acoustic_model} ' +
                           '{l_disambig_fst} ' +
                           'ark:- ark,scp:{ark_file},{scp_file}').format(scale_opts=scale_opts,
                                                 disambig_ids=common.disambig_ids_path,
                                                 tree=common.decision_tree_path,
                                                 acoustic_model=common.acoustic_model_path,
                                                 l_disambig_fst=common.l_disambig_fst_path,
                                                 kaldi_root=common.kaldi_root,
                                                 ark_file=decoded_ark_path,
                                                 scp_file=decoded_scp_path),
                          '--')

    # Run the tokens through the decoding pipeline
    safer_pipeline.copy(tokens_w_key_path, '')

if __name__ == '__main__':
    genGraphs()