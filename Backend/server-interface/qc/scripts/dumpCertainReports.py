# Copyright 2016 Matthias Petursson
# Apache 2.0

import sys
import redis

def run(sessionId):
    name = 'MarosijoModule'

    _redis = redis.StrictRedis(host='localhost', port=6379, db=1)

    report = _redis.get('report/{}/{}'.format(name, sessionId)).decode('utf-8')
    with open('{}/report/{}/{}'.format('/data/eyra/qc_reports', name, sessionId), 'at') as rf:
        print(report, file=rf)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Dump from redis datastore marosijo module reports, certain sessions, can be useful if Celery fails, but the data should always be in memory in redis (not necessarily on file.)
        Very quick and dirty script with a bunch of hardcoded values.
        
        Example usage: for i in {50,104,311}; do python3 dumpCertainReports.py $i; done""")
    parser.add_argument('session_id', type=int)
    args = parser.parse_args()

    run(args.session_id)
