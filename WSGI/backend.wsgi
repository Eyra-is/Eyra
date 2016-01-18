import sys
import os

FPATH=os.path.dirname(os.path.abspath(__file__))
WPATH=os.path.abspath(FPATH + os.sep + '..' 
                            + os.sep + 'Backend' 
                            + os.sep + 'server-interface')
sys.path.insert(0, WPATH)
os.chdir(WPATH)
from network_comms import app as application

