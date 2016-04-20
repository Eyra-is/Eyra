const = dict(
    # redis vars
    host = 'localhost',
    port = 6379,
    broker_db = 0,
    backend_db = 1,
    #
    session_timeout = 25,#15*60, # timeout in seconds, assume session is over, if 15 mins have passed since last query for report 
    task_min_proc_time = 1000000, # minimum time (in microseconds) a processing function should take as to not invoke delays to not put tasks in rapid succession on the queue
    task_delay = 1, # time (in seconds) a process is set to sleep in the event of task taking less than task_min_proc_time
    batch_size = 5, # number of recordings to process at a time (per task)
)