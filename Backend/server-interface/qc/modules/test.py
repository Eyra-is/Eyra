import redis

from celery import Task


# @celery.task(name='qc-process-session')
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

class Derp(object):
    def __call__(self, session_id, indices):
        return self.processBatch(session_id, indices)

    def processBatch(self, session_id, indices):
        import redis
        print('blabla')
        redis = redis.StrictRedis(host='localhost', port=6379, db=1)
        print('in processing batch, {}'.format(indices))
        import time
        time.sleep(4)
        redis.set('report/{}/{}'.format('TestModule', session_id), 
                        {'report':'A GLORIOUS REPORTíþ, {}'.format(indices)})
        if max(indices) > 40:
            return False
        return True


# def processBatch(session_id, indices):
#     import redis
#     print('blabla')
#     redis = redis.StrictRedis(host='localhost', port=6379, db=1)
#     print('in processing batch, {}'.format(indices))
#     import time
#     time.sleep(4)
#     redis.set('report/{}/{}'.format('TestModule', session_id), 
#                     {'report':'A GLORIOUS REPORTíþ, {}'.format(indices)})
#     if max(indices) > 40:
#         return False
#     return True

class TestTask(Task):
    abstract = True
    _redis = None

    #qcProcessSession = app.config['CELERY_QC_PROCESS_FN']

    @property
    def redis(self):
        if self._redis is None:
            self._redis = redis.StrictRedis(host='localhost', port=6379, db=1)

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
    # def __call__(self, session_id, indices):
    #     return self.processBatch(session_id, indices)

    def __init__(self, app):
        """Initialise a TestModule module

        """
        # TODO: use these variables as configs
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=1)

        self.qcProcessSession = app.config['CELERY_QC_PROCESS_FN']
        self.add = app.config['CELERY_ADD']

        # used for keys in redis datastore to identify this module
        self.name = type(self).__name__ 

    def processBatch(self, session_id, indices):
        print('in processing batch, {}'.format(indices))
        import time
        time.sleep(4)
        self.redis.set('report/{}/{}'.format(self.name, session_id), 
                        {'report':'A GLORIOUS REPORTíþ, {}'.format(indices)})
        if max(indices) > 40:
            return False
        return True

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
