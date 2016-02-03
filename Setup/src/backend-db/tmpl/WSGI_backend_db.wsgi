import sys
import os

# http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
sys.stdout=sys.stderr

FPATH=os.path.dirname(os.path.abspath(__file__))
WPATH=os.path.abspath(FPATH + os.sep + '..' 
                            + os.sep + '..' 
                            + os.sep + 'Backend' 
                            + os.sep + 'server-interface')
sys.path.insert(0, WPATH)
os.chdir(WPATH)
from app import app as application

