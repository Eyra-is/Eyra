import redis

#: Relative imports
from util import log
from . import config # get our dict with qc module names -> qc module functions

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

    def __init__(self, app):
        """Initialise a QC handler

        config.activeModules should be a dict containing names : function pointers
        to the QC modules supposed to be used.

        app.config['CELERY_CLASS_POINTER'] should be a function pointer to
        the instance of the celery class created in app from celery_handler.py

        """
        self.modules = {moduleName : module(app) \
                            for moduleName, module in config.activeModules.items()}

        # TODO: use these variables as configs
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=1)

    def getReport(self, session_id) -> dict:
        """Return a quality report for the session ``session_id``, if
        available otherwise we start a background task to process
        currently available recordings.

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
                                "totalStats": {"accuracy": [0.0;1.0]"},
                                "perRecordingStats": [{"recordingId": ...,
                                    "stats": {"accuracy": [0.0;1.0]}}]}
                              }, 
                              ...
                        }
            }

        """
        # TODO: check if session exists

        # individually call get report on each module and grab each ones'
        #   report from the redis datastore
        reports = {}
        for name, module in self.modules.items():
            report = module.getReport(session_id)
            if report is not None:
                reports[name] = report

        if len(reports) > 0:
            return dict(sessionId=session_id, status='processing', modules=reports)
        else:
            return dict(sessionId=session_id, status='started', modules={})
