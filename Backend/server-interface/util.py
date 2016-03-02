# utility functions for server-interface

from datetime import datetime
import sys
import unicodedata
import re

def log(msg, e=None):
    """
    e is an optional exception to log as well
    """
    exceptionText = ''
    if e is not None:
        exceptionText = ' ' + repr(e)
    # http://stackoverflow.com/questions/32550487/how-to-print-from-flask-app-route-to-python-console
    date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(str(date) + ' ' + str(msg) + exceptionText, file=sys.stderr)

def filename(name):
    """
    return name as a valid filename on unix
    change spaces to hyphens and '/' to '\'
    removes trailing/leading whitespace.
    """
    name = unicodedata.normalize('NFKC', name)
    name = re.sub('[-\s]+', '-', name, flags=re.U).strip()
    return name.replace('/', '\\')