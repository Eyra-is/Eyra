import redis
import time

# grab celery_config from dir above this one
# thanks, Alex Martelli, http://stackoverflow.com/a/1054293/5272567
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import celery_config

from celery import Task

class TestTask(Task):
    """TestTask -- A test QC module, placeholder/example module.
    ====================
    
    QC module/base task which does nothing except sleep to imitate processing.

    """
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

    def processBatch(self, name, session_id, indices) -> bool:
        """
        The main processing function of this module.
        This function is called to do processing on a batch
          of recordings from session with session_id, with indices
          in the list of recordings for this session(_id) in
          the redis datastore ('session/session_id/recordings').
        name is the name to use to write the report to redis datastore
          at 'report/name/session_id'

        This particular processing function, only sleeps for 4 seconds
          to imitate processing done in a real QC module.

        Return False or raise an exception if something is wrong (and
        this should not be called again.)
        """
        print('In processing batch, indices: {}'.format(indices))
        time.sleep(4)
        self.redis.set('report/{}/{}'.format(name, session_id), 
                        {'report':'A TEST REPORT, indices: {}'.format(indices)})
        return True
