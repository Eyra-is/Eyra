import redis

# grab celery_config from dir above this one
# thanks, Alex Martelli, http://stackoverflow.com/a/1054293/5272567
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import celery_config

from celery import Task

class DummyTask(Task):
    """DummyTask - Do no quality control
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
        Dummy method, always sets same report in redis datastore, i.e.
            {"totalStats": {"accuracy":0},
             "report" : "No report (dummy)."}
            with key: report/name/session_id
        """
        self.redis.set('report/{}/{}'.format(name, session_id), 
                        {"totalStats": {"accuracy":0},
                         "report" : "No report (dummy)."})
        return False