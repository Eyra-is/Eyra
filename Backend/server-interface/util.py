# utility functions for server-interface

from datetime import datetime
import sys

def log(arg):
    # http://stackoverflow.com/questions/32550487/how-to-print-from-flask-app-route-to-python-console
    date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(str(date) + ' ' + str(arg), file=sys.stderr)