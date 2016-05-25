import sh
import os
import sys
import json
import time

# mv out of qc/script directory and do relative imports from there.
parParDir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.append(parParDir)
from qc.config import activeModules
import qc.celery_config as celery_config
from util import DbWork, simpleLog
sys.path.remove(parParDir)
del parParDir

def runQC(sleep_between, avoid_timeout):
    """
    Runs QC on all recordings which haven't been analyzed by QC yet.
    """
    dbWork = DbWork()

    numSessions = dbWork.sessionCount()
    start = time.time()
    for i in range(1, numSessions + 1):
        if (qcDumpRecCountBySession(i) < dbWork.recCountBySession(i)):
            sh.curl('-k', 'https://localhost/backend/qc/report/session/{}'.format(i))
            time.sleep(sleep_between)

        # also routinely check unfinished sessions already checked to avoid a timeout
        end = time.time()
        if (end - start) > avoid_timeout * 60:
            start = time.time()
            for j in range(1, i + 1):
                # assume any session with under this (10) amount of recs would have completed before this time
                if (dbWork.recCountBySession(j) > 10 and qcDumpRecCountBySession(j) < dbWork.recCountBySession(j)):
                    sh.curl('-k', 'https://localhost/backend/qc/report/session/{}'.format(j))
                    time.sleep(0.2)

def qcDumpRecCountBySession(sessionId):
    """
    Returns the minimum (of all active modules) number of recordings with a qc report dumped on disk by session.
    e.g. if there is no report for any active module, returns 0.

    Parameters:
        sessionId       id of session
    """
    minimum = sys.maxsize
    for key, module in activeModules.items():
        dumpPath = '{}/report/{}/{}'.format(celery_config.const['qc_report_dump_path'],
                                            module['name'],
                                            sessionId)
        try:
            with open(dumpPath, 'r') as f:
                reports = f.read().splitlines() # might be more than one, if a timeout occurred and recording was resumed
                # sum the recordings of all the reports (usually only one)
                totalRecs = 0
                for report in reports:
                    report = json.loads(report)
                    try:
                        totalRecs += len(report['perRecordingStats'])
                    except KeyError as e:
                        # probably a module which doesn't have perRecordingStats, allow it.
                        totalRecs = sys.maxsize if totalRecs == 0 else totalRecs
                        break
                minimum = min(minimum, totalRecs)
        except FileNotFoundError as e:
            return 0

    return minimum if minimum != sys.maxsize else 0

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Runs QC on all recordings which QC hasn't been run on yet.""")
    parser.add_argument('--sleep_between', type=int, nargs='?', default=5, help='Time to sleep between curl requests on server in seconds.')
    parser.add_argument('--avoid_timeout', type=int, nargs='?', default=5, help='Recheck old sessions to avoid a timeout at this interval in minutes. Only check sessions with at least 10 (or something) recordings.')
    args = parser.parse_args()

    runQC(args.sleep_between, args.avoid_timeout)

