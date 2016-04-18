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
        # mysql starts counting at 1. These tok_keys should correspond to mysql id's
        #   of tokens (because this is crucial, since the cleanup module relies
        #   on the ids, we make sure to verify this by querying the database for each token
        #   see util.DbWork)
        dbWork = DbWork()
        tokenKey = 1
        for token in tokensF:
            token = token.rstrip('\n')
            tokenInts = common.symToInt(token.lower())
            if dbWork.verifyTokenId(tokenKey, token):
                tokensLines.append('{} {}'.format(tokenKey, tokenInts))
            else:
                raise ValueError('Could not verify token, "{}" with id {}.'.format(token, tokenKey))
            tokenKey += 1

    simpleLog('Compiling the decoding graphs (files {} and {}).  This will take a long time.'
              .format(graphsArkPath, graphsScpPath))

    compileTrainGraphsFsts(
        makeUtteranceFsts(
            common.phoneLmPath,
            common.symbolTablePath,
            _in='\n'.join(tokensLines),
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
        Writes to qc/modules/MarosijoModule/local directory.""")
    parser.add_argument('--concurrency', '-c', type=int, default=1,
                        help='How many processes to use')
    parser.add_argument('tokens_path', type=str, help='Path to token file')
    args = parser.parse_args()

    genGraphs(args.tokens_path, modulePath)
