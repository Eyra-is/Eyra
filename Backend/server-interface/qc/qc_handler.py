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
#     Robert Kjaran <robert@kjaran.com>

import redis
import datetime
import json

#: Relative imports
from util import log
from . import config # get our dict with qc module names & qc module functions
from . import celery_config

class QcError(Exception):
    """QcError
    ==========

    Trouble in paradise. Raised if QC experienced a critical error.

    """
    pass

class QcHandler(object):
    """QcHandler
    ============

    Class for handling quality control reporting.

    Its only public method is :meth:`getReport`. See its docstring for
    details.

    Use the config.py file to adjust which modules you want to be active
    in the QC.

    Usage:

    >>> qc = QcHandler(app)
    >>> qc.getReport(1)
    {'sessionId': 1, 'status': 'started', 'modules':{}}
    ... wait ...
    >>> qc.getReport(1)
    {"sessionId": 1,
     "status": "processing",
     "modules"  {
        "marosijo" :  {
                        "totalStats": {"accuracy": [0.0;1.0]"},
                        "perRecordingStats": [{"recordingId": ...,
                            "stats": {"accuracy": [0.0;1.0]}}]}
                      }, 
                      ...
                }
    }

    """

    def __init__(self, app, dbHandler):
        """Initialise a QC handler

        config.activeModules should be a dict containing names : function pointers
        to the QC modules supposed to be used.

        app.config['CELERY_CLASS_POINTER'] should be a function pointer to
        the instance of the celery class created in app from celery_handler.py

        """
        self.modules = {module['name'] : module['processFn'] \
                            for k, module in config.activeModules.items()}

        self.dbHandler = dbHandler # grab database handler from app to handle MySQL database operations

        self.redis = redis.StrictRedis(
            host=celery_config.const['host'], 
            port=celery_config.const['port'], 
            db=celery_config.const['backend_db'])

    def _updateRecordingsList(self, session_id) -> None:
        """
        Update the list of recordings for this session(_id) in 
        the redis datastore. Query the MySQL database and write
        out the recordings there (for this session) to the redis datastore.

        Redis key format: session/session_id/recordings
        Redis value format (same as from dbHandler.getRecordingsInfo return value):
            [{"recId": ..., "token": str, "recPath": str}, ..]
        Where the recPaths are directly from the MySQL database (relative paths to
        server-interface/)

        Example:
            'session/2/recordings' -> 
                [{"recId":2, "token":'hello', "recPath":'recordings/session_2/user_2016-03-09T15:42:29.005Z.wav'},
                {"recId":2, "token":'hello', "recPath":'recordings/session_2/user_2016-03-09T15:42:29.005Z.wav'}]
        """
        recsInfo = self.dbHandler.getRecordingsInfo(session_id)
        if len(recsInfo) > 0:
            self.redis.set('session/{}/recordings'.format(session_id), recsInfo)

    def getReport(self, session_id) -> dict:
        """Return a quality report for the session ``session_id``, if
        available otherwise we start a background task to process
        currently available recordings.
        Keeps a timestamp at 'session/session_id/timestamp' in redis datastore
          representing the last time we were queried for said session.

        Parameters:

          session_id   ...

        Returned dict if the QC report is not available, but is being
        processed:

            {"sessionId": ...,
             "status": "started",
             "modules":{}}

        Returned dict definition if no QC module is active:

            {"sessionId": ...,
             "status": "inactive",
             "modules":{}}

        Returned dict definition:

            {"sessionId": ...,
             "status": "processing",
             "modules"  {
                "module1" :  {
                                "totalStats": {"accuracy": [0.0;1.0]"}
                                [, "perRecordingStats": [
                                        {"recordingId": ...,
                                            "stats": {"accuracy": [0.0;1.0]}
                                        },
                                        ...]}
                                ]
                              }, 
                              ...
                        }
            }

        (see client-server API for should be same definition of return)

        """
        # check if session exists
        if not self.dbHandler.sessionExists(session_id):
            return None

        # no active QC
        if len(self.modules) == 0:
            return dict(sessionId=session_id, status='inactive', modules={})

        # see if there is a returning user to this session, in which case, start
        # counting at the index after the last made recording
        # (slistIdx is not used here unless there isn't a report)
        # if in qc_offline mode (post-processing), this is not really useful and
        # can be harmful, since the recordings list doesn't change now.
        recsInfo = self.redis.get('session/{}/recordings'.format(session_id))
        if recsInfo and not celery_config.const['qc_offline_mode']:
            recsInfo = json.loads(recsInfo.decode('utf-8'))
            slistIdx = len(recsInfo)
        else:
            slistIdx = 0

        # always update the sessionlist on getReport call, there might be new recordings
        self._updateRecordingsList(session_id)

        # set the timestamp, for the most recent query (this one) of this session
        self.redis.set('session/{}/timestamp'.format(session_id),
            datetime.datetime.now())

        # attempt to grab report for each module from redis datastore.
        #   if report does not exist, add a task for that session to the celery queue
        reports = {}
        for name, processFn in self.modules.items():
            report = self.redis.get('report/{}/{}'.format(name, session_id))
            if report:
                reports[name] = json.loads(report.decode("utf-8")) # redis.get returns bytes, so we decode into string
            else:
                # first check if we are already working on this session with this module, 
                # in which case do nothing here
                processing = self.redis.get('session/{}/processing'.format(session_id))
                if processing:
                    continue

                # check to see if we have any reports dumped on disk, in which case continue
                # where they left off
                qcReportPath = '{}/report/{}/{}'.format(celery_config.const['qc_report_dump_path'],
                                                        name,
                                                        session_id)
                try:
                    with open(qcReportPath, 'r') as f:
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
                                break
                        if totalRecs != 0:
                            slistIdx = totalRecs
                except FileNotFoundError as e:
                    pass

                # start the async processing
                processFn.delay(name, session_id, slistIdx, celery_config.const['batch_size'])

        if len(reports) > 0:
            return dict(sessionId=session_id, status='processing', modules=reports)
        else:
            return dict(sessionId=session_id, status='started', modules={})
