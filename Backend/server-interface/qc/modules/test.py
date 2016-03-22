import redis
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import celery_config

from celery import Task

class TestTask(Task):
    abstract = True
    _redis = None

    @property
    def redis(self):
        if self._redis is None:
            self._redis = redis.StrictRedis(
                host=celery_config.const['host'], 
                port=celery_config.const['port'], 
                db=celery_config.const['backend_db'])

        return self._redis

    def processBatch(self, session_id, indices):
        print('in processing batch, {}'.format(indices))
        import time
        time.sleep(4)
        self.redis.set('report/{}/{}'.format('TestModule', session_id), 
                        {'report':'A GLORIOUS REPORTíþ, {}'.format(indices)})
        if max(indices) > 40:
            return False
        return True

class TestModule(object):
    """TestModule -- A test QC module, placeholder/example module.
    ====================
    
    QC module which does nothing except sleep to imitate processing.

    """

    def __init__(self, app):
        """Initialise a TestModule module

        """
        # TODO: use these variables as configs
        self.redis = redis.StrictRedis(
            host=celery_config.const['host'], 
            port=celery_config.const['port'], 
            db=celery_config.const['backend_db'])

        self.qcProcessSession = app.config['CELERY_QC_PROCESS_FN']
        self.add = app.config['CELERY_ADD']

        # used for keys in redis datastore to identify this module
        self.name = type(self).__name__ 

    def getReport(self, session_id: int) -> dict:
        """Returns a QC report

        If session with ``session_id`` exists:
          If in datastore: Read from datastore and return
          Otherwise: Return started message and start the task if not started

        Otherwise: Return raise/signal an error

        """

        # TODO: check if session exists
        report = self.redis.get('report/{}/{}'.format(self.name, session_id))
        if report is not None:
            return report\
                    .decode("utf-8") # redis.get returns bytes, so we decode into string
        else:
            #print(self.add.delay(1,2).get())
            self.qcProcessSession.delay(session_id, None, 0, 5)
            # self.qcProcessSession.apply_async(
            #    args=[session_id, self.processBatch, 0])
            return None
