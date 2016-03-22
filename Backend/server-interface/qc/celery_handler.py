from celery import Celery

from .modules.test import TestTask

#def __init__(self, app):
host = 'localhost'
port = 6379
broker_db = 0
backend_db = 1

# TODO: Move to a config file
# app.config['CELERY_BROKER_URL'] = 'redis://{}:{}/{}'\
#                                     .format(host, port, broker_db)
# app.config['CELERY_RESULT_BACKEND'] = 'redis://{}:{}/{}'\
#                                         .format(host, port, backend_db)

broker = 'redis://{}:{}/{}'.format(host, port, broker_db)

# def make_celery(app):
#     celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
#     celery.conf.update(app.config)
#     TaskBase = celery.Task
#     class ContextTask(TaskBase):
#         abstract = True
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#     celery.Task = ContextTask
#     return celery

# celery = make_celery(app)

celery = Celery(broker=broker)
celery.conf.update(
    CELERY_RESULT_BACKEND='redis://{}:{}/{}'.format(host, port, backend_db))

@celery.task
def add(x,y):
    print(str(x),str(y))
    return x+y

@celery.task(base=TestTask)
def qcProcessSession(sessionId, processFn, slistIdx=0, batchSize=5):
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
    print('goodbye cruel world')
    #print('in processing batch, {}'.format(6646564654646))
    # import time
    # time.sleep(4)
    # qcProcessSession.getRedis.set('report/{}/{}'.format('TestModule', sessionId), 
    #                 {'report':'A GLORIOUS REPORTíþ, {}'.format(5465465465464654)})

    result = qcProcessSession.processBatch(sessionId, list(range(slistIdx, slistIdx+batchSize)))
    if result:
       qcProcessSession.apply_async(
           args=[sessionId, processFn, slistIdx+batchSize, batchSize])

# @celery.task(name='sum-of-two-numbers')
# def qcProcessSession(sessionId, processFn, slistIdx=0, batchSize=5):
#     """
#     Goes through the sessionList, containing a list of all current
#     recordings of this session, in the backend continuing from
#     slistIdx. 

#     Performs processFn which is a function pointer to the function
#     which does the processing, processFn must take exactly 2 arguments
#     the first is sessionId, second is a list of indices of recordings to process. 
#     processFn is responsible for putting the results on the correct format in the
#     report in the redis datastore. Obviously, processFn needs to be a
#     synchronous function.

#     Only processes batchSize recs at a time, until calling itself recursively
#     with the updated slistIdx (and by that placing itself at the back
#     of the celery queue), look at instagram, that's how they do it xD
#     """
#     result = processFn(sessionId, list(range(slistIdx, slistIdx+batchSize)))
#     #if result:
#     #    qcProcessSession.apply_async(
#     #        args=[sessionId, processFn, slistIdx+batchSize, batchSize])

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