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

import sh
import tempfile
import os
import re
import sys
from multiprocessing import Process

# mv out of qc/script directory and do relative imports from there.
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.append(newPath)
from qc.modules.MarosijoModule.MarosijoModule import MarosijoCommon
from util import DbWork, simpleLog
sys.path.remove(newPath)
del newPath

def genGraphs(tokensPath, modulePath=None, graphsArkPath=None, graphsScpPath=None):
    """
    Generate decoding graphs for each token for our Marosijo module.
    
    Only needs to be run once (for each version of the tokens).

    Parameters:
        tokensPath      path to the token list on format "tokId token"
        modulePath      absolute path to the module root (e.g. /.../qc/modules/MarosijoModule)
        graphsArkPath   absolute path to where .ark file should be saved
        graphsScpPath   absolute path to where .scp file should be saved  
    """
    if modulePath is None:
        modulePath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                  os.path.pardir,
                                                  'modules', 'MarosijoModule'))
    os.makedirs(os.path.join(modulePath, 'local'), exist_ok=True)

    if graphsArkPath is None:
        graphsArkPath = os.path.join(modulePath, 'local', 'graphs.ark')
    if graphsScpPath is None:
        graphsScpPath = os.path.join(modulePath, 'local', 'graphs.scp')

    common = MarosijoCommon(os.path.join(modulePath, 'local'), graphs=False)

    #: Shell commands
    makeUtteranceFsts = sh.Command(os.path.join(os.path.dirname(__file__),
                                                './marosijo_make_utterance_fsts.sh'))
    fstEnv = os.environ.copy()
    fstEnv['PATH'] = '{}/tools/openfst/bin:{}'.format(common.kaldiRoot, fstEnv['PATH'])
    print(fstEnv['PATH'])
    makeUtteranceFsts = makeUtteranceFsts.bake(_env=fstEnv)
    compileTrainGraphsFsts = sh.Command('{}/src/bin/compile-train-graphs-fsts'
                                        .format(common.kaldiRoot))

    tokensLines = []
    with open(tokensPath) as tokensF:
        # These tok_keys should correspond to mysql id's
        #   of tokens (because this is crucial, since the cleanup module relies
        #   on the ids, we make sure to verify this by querying the database for each token
        #   see util.DbWork)
        dbWork = DbWork()
        for line in tokensF:
            line = line.rstrip('\n')
            tokenKey = line.split(' ')[0]
            token = ' '.join(line.split(' ')[1:]) # split(' ') needed because split() rstrips the space by default
            tokenInts = common.symToInt(token.lower())
            if dbWork.verifyTokenId(tokenKey, token):
                tokensLines.append('{} {}'.format(tokenKey, tokenInts))
            else:
                raise ValueError('Could not verify token, "{}" with id {}.'.format(token, tokenKey))

    simpleLog('Compiling the decoding graphs (files {} and {}).  This will take a long time.'
              .format(graphsArkPath, graphsScpPath))

    compileTrainGraphsFsts(
        makeUtteranceFsts(
            common.phoneLmPath,
            common.symbolTablePath,
            _in='\n'.join(tokensLines) + '\n',
            _piped=True,
            _err=simpleLog
        ),
        '--verbose=4',
        '--batch-size=1',
        '--transition-scale=1.0',
        '--self-loop-scale=0.1',
        '--read-disambig-syms={}'.format(common.disambigIntPath),
        '{tree}'.format(tree=common.treePath),
        common.acousticModelPath,
        common.lexiconFstPath,
        'ark:-',
        'ark,scp:{ark},{scp}'.format(ark=graphsArkPath,
                                     scp=graphsScpPath),
        _err=simpleLog
    )

    # update the paths to the .ark file in .scp to be relative to the module root directory
    # sh.sed("-i", "s:{}/::g".format(modulePath), graphsScpPath)

if __name__ == '__main__':
    import argparse

    modulePath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              os.path.pardir,
                                              'modules', 'MarosijoModule'))

    parser = argparse.ArgumentParser(description="""
        Generate decoding graphs for each token for our Marosijo module.
        Only needs to be run once (for each version of the tokens).
        Writes to qc/modules/MarosijoModule/local directory, if no path specified.""")
    parser.add_argument('tokens_path', type=str, help='Path to token file')
    parser.add_argument('graphs_ark_path', type=str, nargs='?', help='Path to generated .ark file')
    parser.add_argument('graphs_scp_path', type=str, nargs='?', help='Path to generated .scp file')
    args = parser.parse_args()

    genGraphs(  args.tokens_path, 
                modulePath, 
                os.path.abspath(args.graphs_ark_path), 
                os.path.abspath(args.graphs_scp_path)
    )

