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
import os
import sys
import json
import time
import redis

# mv out of qc/script directory and do relative imports from there.
parParDir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.append(parParDir)
from qc.config import activeModules
import qc.celery_config as celery_config
from util import DbWork
sys.path.remove(parParDir)
del parParDir

dbWork = DbWork()
_redis = redis.StrictRedis(
            host=celery_config.const['host'], 
            port=celery_config.const['port'], 
            db=celery_config.const['backend_db'])
verbose = False

def runQC(from_session, to_session, sleep_between, avoid_timeout):
    """
    Runs QC on recordings which haven't been analyzed by QC yet.
    """
    if to_session is None:
        to_session = dbWork.highestSessionId()

    if to_session == 'stdin':
        sesRange = sys.stdin
        prevSes = []
    else:
        sesRange = range(from_session, min(to_session + 1, dbWork.highestSessionId()))

    start = time.time()
    totalDiff = 0
    for i in sesRange:
        # if in individual_sessions mode, strip newline
        if type(i) is str:
            i = i.strip()
        if to_session == 'stdin':
            prevSes.append(i)

        print('Processing session {}'.format(i))
        recsOnDisk = qcDumpRecCountBySession(i)
        recsInRedis = qcRedisRecCountBySession(i)
        recsInDb = dbWork.recCountBySession(i)
        recsDone = max(recsInRedis, recsOnDisk)
        if verbose:
            print('Recs done: {}'.format(recsDone))
            print('..in redis: {}'.format(recsInRedis))
            print('..on disk: {}'.format(recsOnDisk))
            print('..recs in db: {}'.format(recsInDb))
        if (recsDone < recsInDb):
            print('Querying QC for session {}'.format(i))
            sh.curl('-k', 'https://localhost/backend/qc/report/session/{}'.format(i))
            time.sleep(sleep_between)
            diff = dbWork.recCountBySession(i)-recsDone
            totalDiff+=diff
            print('Diff:',diff)

        # also routinely check unfinished sessions already checked to avoid a timeout
        end = time.time()
        if (end - start) > avoid_timeout:
            start = time.time()
            if to_session == 'stdin':
                reQuerySessions(from_session, to_session, prevSes)
            else:
                reQuerySessions(from_session, i)
    print('totalDiff:',totalDiff)

def reQuerySessions(from_session, to_session, prevSes=None):
    if to_session is None:
        to_session = dbWork.highestSessionId()

    if to_session == 'stdin':
        secRange = prevSes
    else:
        secRange = range(from_session, min(to_session + 1, dbWork.highestSessionId()))

    print('Doing a re-query of previous sessions up to {}'.format(to_session))
    for j in secRange:
        if max(qcRedisRecCountBySession(j), qcDumpRecCountBySession(j)) < dbWork.recCountBySession(j):
            sh.curl('-k', 'https://localhost/backend/qc/report/session/{}'.format(j))
            time.sleep(0.01)

def qcRedisRecCountBySession(sessionId):
    """
    Returns the minimum (of all active modules) number of recordings with a qc report in redis datastore by session.
    e.g. if there is no report for any active module, returns 0.

    Parameters:
        sessionId       id of session
    """
    minimum = sys.maxsize
    for key, module in activeModules.items():
        reportPath = 'report/{}/{}'.format(module['name'], sessionId)
        try:
            totalRecs = 0
            report = json.loads(_redis.get(reportPath).decode('utf-8'))
            try:
                totalRecs += len(report['perRecordingStats'])
            except KeyError as e:
                # probably a module which doesn't have perRecordingStats, allow it.
                totalRecs = sys.maxsize if totalRecs == 0 else totalRecs
            minimum = min(minimum, totalRecs)
        except AttributeError as e:
            return 0

    return minimum if minimum != sys.maxsize else 0

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
                    if report == '':
                        # robustness to extra newlines
                        continue
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

def calcTotalQCDone():
    """
    Returns the number of recordings analysed by qc and dumped on disk.
    """
    dbWork = DbWork()
    numSessions = dbWork.highestSessionId()
    total = 0
    print('Session','NumRecs','QCAnalysed')
    for i in range(1, numSessions + 1):
        print('{}\t'.format(i),'{}\t'.format(dbWork.recCountBySession(i)),'{}\t'.format(qcDumpRecCountBySession(i)))
        total += qcDumpRecCountBySession(i)
    return total

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Runs QC on recordings which QC hasn't been run on yet. 
        You probably want to modify ../celery_config.py and set 'qc_offline_mode' 
        and 'qc_big_batch_mode' to True. 
        See more detailed instructions in DEVELOPER.md.""")
    parser.add_argument('--from_session', type=int, nargs='?', default=1, help='Session to start querying QC.')
    parser.add_argument('--to_session', type=int, nargs='?', default=None, help='Last session queried.')
    parser.add_argument('--sleep_between', type=float, nargs='?', default=5, help='Time to sleep between curl requests on server in seconds.')
    parser.add_argument('--avoid_timeout', type=float, nargs='?', default=300, help='Recheck old sessions to avoid a timeout at this interval in seconds.')
    parser.add_argument('--individual_sessions', action='store_true', help='Uses all sessions in stdin (1 per line) and queries them. Including this flag means to_session and from_session are ignored.')
    parser.add_argument('--requery_sessions', action='store_true', help='Queries all sessions from_session and to_session (this is also done automatically during a normal run, but can be done specifically here). Cannot be run with individual_sessions flag. Including this flag means avoid_timeout and sleep_between are ignored.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Increase output verbosity.')
    args = parser.parse_args()

    if args.verbose:
        verbose = True

    if args.individual_sessions:
        runQC(None, 'stdin', args.sleep_between, args.avoid_timeout)
    elif args.requery_sessions:
        reQuerySessions(args.from_session, args.to_session)
    else:
        runQC(args.from_session, args.to_session, args.sleep_between, args.avoid_timeout)
        #print(calcTotalQCDone())
