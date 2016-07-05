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

def genGraphs(tokens_path, module_path=None, decoded_ark_path=None, decoded_scp_path=None):
    """
    Generate decoding graphs for each token for our Cleanup module.

    Only needs to be run once (for each version of the tokens).

    Parameters:
        tokens_path         path to the token list on format "tokId token"
        module_path         absolute path to the module root (e.g. /.../qc/modules/CleanupModule)
        decoded_ark_path    absolute path to where .ark file should be saved
        decoded_scp_path    absolute path to where .scp file should be saved   
    """

    if module_path is None:
        module_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   os.path.pardir,
                                                   'modules', 'CleanupModule'))
    if decoded_ark_path is None:
        os.makedirs(os.path.join(module_path, 'local'), exist_ok=True)
        decoded_ark_path = os.path.join(module_path, 'local', 'graphs.ark')
    if decoded_scp_path is None:
        os.makedirs(os.path.join(module_path, 'local'), exist_ok=True)
        decoded_scp_path = os.path.join(module_path, 'local', 'graphs.scp')

    # init constants and open files
    common = CleanupCommon()

    transition_scale = '--transition-scale=1.0'
    self_loop_scale = '--self-loop-scale=0.1'

    # create our commands for sh
    make_utterance_fsts = sh.Command('./make_utterance_fsts.pl')
    compile_train_graphs_fsts = sh.Command('{}/src/bin/compile-train-graphs-fsts'
                                            .format(os.path.join(module_path, common.kaldi_root)))

    #: Mapping from symbols to integer ids
    sym_id_path = os.path.join(module_path, common.sym_id_path)
    with open(sym_id_path, 'rt') as sf:
        sym_id_map = dict(line.strip().split() for line in sf)

    #: Mapping from integer ids to symbols
    id_sym_map = dict((val, key) for key, val in sym_id_map.items())

    # TODO: try to eliminate the use of tempfiles (mkfifo)
    _, tokens_w_id_path = tempfile.mkstemp(prefix='qc')
    with open(tokens_path, 'r') as tokens_f, \
            open(tokens_w_id_path, 'wt') as tokens_with_id_f:
        # mysql starts counting at 1. These tok_keys should correspond to mysql id's
        #   of tokens (because this is crucial, since the cleanup module relies
        #   on the ids, we make sure to verify this by querying the database for each token
        #   see util.DbWork)
        dbWork = DbWork()
        for line in tokens_f.read().splitlines():
            tok_key = line.split(' ')[0]
            token = ' '.join(line.split(' ')[1:]) # split(' ') needed because split() rstrips the space by default
            token_ids = ' '.join(common.sym_id_map.get(tok.lower(), common.oov_id) for
                                 tok in token.split())
            if dbWork.verifyTokenId(tok_key, token):
                print('{} {}'.format(tok_key, token_ids),
                      file=tokens_with_id_f)
            else:
                raise ValueError('Token not verified, %s with id %d.' % (token, int(tok_key)))

    # create a pipe using sh, output of make_utterance_fsts piped into compile_train_graphs
    # piping in contents of tokens_w_id_path and writing to decoded_{ark,scp}_path
    compile_train_graphs_fsts( 
        make_utterance_fsts(
            sh.cat(
                tokens_w_id_path,
                _piped=True,
                _err=simpleLog
            ),
            '{top_words}'.format(top_words=os.path.join(module_path, common.top_words_path)),
            _piped=True,
            _err=simpleLog
        ),
        transition_scale,
        self_loop_scale,
        '--read-disambig-syms={}'.format(os.path.join(module_path, common.disambig_ids_path)),
        '{tree}'.format(tree=os.path.join(module_path, common.decision_tree_path)),
        os.path.join(module_path, common.acoustic_model_path),
        os.path.join(module_path, common.l_disambig_fst_path),
        'ark:-',
        'ark,scp:{ark_file},{scp_file}'.format( ark_file=decoded_ark_path,
                                                scp_file=decoded_scp_path),
        _err=simpleLog
    )

if __name__ == '__main__':
    import argparse

    modulePath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              os.path.pardir,
                                              'modules', 'CleanupModule'))

    parser = argparse.ArgumentParser(description="""
        Generate decoding graphs for each token for our Cleanup module.
        Only needs to be run once (for each version of the tokens).
        Writes to qc/modules/CleanupModule/local directory if no path specified.""")
    parser.add_argument('tokens_path', type=str, help='Path to token file')
    parser.add_argument('graphs_ark_path', type=str, nargs='?', help='Path to generated .ark file')
    parser.add_argument('graphs_scp_path', type=str, nargs='?', help='Path to generated .scp file')
    args = parser.parse_args()

    genGraphs(  args.tokens_path, 
                modulePath, 
                os.path.abspath(args.graphs_ark_path), 
                os.path.abspath(args.graphs_scp_path)
    )

