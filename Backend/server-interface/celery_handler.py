from celery import Celery
from celery.contrib.methods import task
import redis

class CeleryHandler:
    def __init__(self, app):
        self.host = 'localhost'
        self.port = 6379
        self.db = 0

        # TODO: Move to a config file
        app.config['CELERY_BROKER_URL'] = 'redis://{}:{}/{}'\
                                            .format(self.host, self.port, self.db)
        app.config['CELERY_RESULT_BACKEND'] = 'redis://{}:{}/{}'\
                                                .format(self.host, self.port, self.db)

        def make_celery(app):
            celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
            celery.conf.update(app.config)
            TaskBase = celery.Task
            class ContextTask(TaskBase):
                abstract = True
                def __call__(self, *args, **kwargs):
                    with app.app_context():
                        return TaskBase.__call__(self, *args, **kwargs)
            celery.Task = ContextTask
            return celery

        self.celery = make_celery(app)

        self.redis = redis.StrictRedis(host=self.host, port=self.port, db=self.db)

    @task()
    def qcProcessSession(self, sessionId, slistIdx):
        """
        Goes through the sessionList, containing a list of all current
        recordings of this session, in the backend continuing from
        slistIdx. 
        Only processes NUMRECS at a time, until calling itself recursively
        with the updated slistIdx (and by that placing itself at the back
        of the celery queue), look at instagram, that's how they do it xD
        """
        self.redis.set('report/{}'.format(sessionId), {'report':'A GLORIOUS REPORT'})