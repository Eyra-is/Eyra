from celery import Celery

from .modules.test import TestTask
from . import celery_config

host = celery_config.const['host']
port = celery_config.const['port']
broker_db = celery_config.const['broker_db']
backend_db = celery_config.const['backend_db']


broker = 'redis://{}:{}/{}'.format(host, port, broker_db)

celery = Celery(broker=broker)
celery.conf.update(
    CELERY_RESULT_BACKEND='redis://{}:{}/{}'.format(host, port, backend_db)
)

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
