from celery import Celery, current_app
from celery.contrib.methods import task, task_method

class CeleryHandler(object):
    def __init__(self, app):
        self.host = 'localhost'
        self.port = 6379
        self.broker_db = 0
        self.backend_db = 1

        # TODO: Move to a config file
        app.config['CELERY_BROKER_URL'] = 'redis://{}:{}/{}'\
                                            .format(self.host, self.port, self.broker_db)
        app.config['CELERY_RESULT_BACKEND'] = 'redis://{}:{}/{}'\
                                                .format(self.host, self.port, self.backend_db)

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

    def getCelery(self):
        return self.celery


    @current_app.task(filter=task_method)
    def add(self,x,y):
        print(str(x),str(y))
        return x+y

    @task()
    def qcProcessSession(self, sessionId, processFn, slistIdx=0, batchSize=5):
        """
        Goes through the sessionList, containing a list of all current
        recordings of this session, in the backend continuing from
        slistIdx. 

        Performs processFn which is a function pointer to the function
        which does the processing, processFn must take exactly 2 arguments
        the first is sessionId, second is a list of indices of recordings to process. 
        processFn is responsible for putting the results on the correct format in the
        report in the redis datastore. Obviously, processFn needs to be a
        synchronous function.

        Only processes batchSize recs at a time, until calling itself recursively
        with the updated slistIdx (and by that placing itself at the back
        of the celery queue), look at instagram, that's how they do it xD
        """
        result = processFn(sessionId, list(range(slistIdx, slistIdx+batchSize)))
        # if result:
        #     self.qcProcessSession.apply_async(
        #         args=[sessionId, processFn, slistIdx+batchSize, batchSize])

# test the class
# if __name__ == '__main__':
#     import os,sys,inspect
#     currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#     parentdir = os.path.dirname(currentdir)
#     sys.path.insert(0,parentdir) 

#     from app import app
#     c = CeleryHandler(app)
#     res = c.add.delay(3,4)
#     print(res.get())