import sh
import tempfile
import os
import re
import sys

# mv out of qc/script directory and do relative imports from there.
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.append(newPath)
from qc.modules.CleanupModule.CleanupModule import CleanupCommon
from util import DbWork, simpleLog
sys.path.remove(newPath)
del newPath

def genGraphs():
    """
    Generate decoding graphs for each token for our Cleanup module.

    Only needs to be run once (for each version of the tokens).
    """

    cleanup_path = '../modules/CleanupModule/'
    os.makedirs(cleanup_path + 'local', exist_ok=True)
    # relative paths, need to prepend cleanup_path where appropriate
    decoded_ark_path = 'local/decoded_graphs.ark'
    decoded_scp_path = 'local/decoded_graphs.scp'
    tokens_path = '../../../db/src/mim_malr_tokens_plus_rare.txt'

    # init constants and open files
    common = CleanupCommon()

    transition_scale = '--transition-scale=1.0'
    self_loop_scale = '--self-loop-scale=0.1'

    # create our commands for sh
    make_utterance_fsts = sh.Command('./make_utterance_fsts.pl')
    compile_train_graphs_fsts = sh.Command('{}/src/bin/compile-train-graphs-fsts'
                                            .format(cleanup_path+common.kaldi_root))

    #: Mapping from symbols to integer ids
    sym_id_path = cleanup_path + common.sym_id_path
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

    # create a pipe using sh, output of make_utterance_fsts piped into compile_train_graphs
    # piping in contents of tokens_w_key_path and writing to decoded_{ark,scp}_path
    compile_train_graphs_fsts( 
        make_utterance_fsts(
            sh.cat(
                tokens_w_key_path,
                _piped=True,
                _err=simpleLog
            ),
            '{top_words}'.format(top_words=cleanup_path+common.top_words_path),
            _piped=True,
            _err=simpleLog
        ),
        transition_scale,
        self_loop_scale,
        '--read-disambig-syms={}'.format(cleanup_path+common.disambig_ids_path),
        '{tree}'.format(tree=cleanup_path+common.decision_tree_path),
        cleanup_path+common.acoustic_model_path,
        cleanup_path+common.l_disambig_fst_path,
        'ark:-',
        'ark,scp:{ark_file},{scp_file}'.format( ark_file=cleanup_path+decoded_ark_path,
                                                scp_file=cleanup_path+decoded_scp_path),
        _err=simpleLog
    )

    # update the paths to the .ark file in .scp to be relative to the module root directory
    # i.e. Cleanup/
    sh.sed("-i", 
           "s/{}/{}/g".format(re.escape(cleanup_path+decoded_ark_path), 
                              re.escape(decoded_ark_path)),
           cleanup_path+decoded_scp_path)

if __name__ == '__main__':
    if len(sys.argv) != 1:
        print( 
"Usage:\
   python3 %s\n\n\
   Generate decoding graphs for each token for our Cleanup module.\n\
   Only needs to be run once (for each version of the tokens).\n\
   Writes to qc/modules/CleanupModule/local directory.\n" % sys.argv[0]
        )
    else:
        genGraphs()