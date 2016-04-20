# QC - quality control

This QC uses Celery and a task chaining system to handle load and remain scalable (that's the idea anyway). By processing only a batch of recordings at a time, and then putting the continuation back on the queue as a task.

## Firing up the QC

The QC needs a worker running constantly. This is for Celery. You need to install Celery and redis-server, this should be in `Setup/src/backend-qc/*.deps`. Running `./Setup/setup.sh --backend-qc` should install those for you.
Then, the worker is run automatically in the background, (see `Setup/src/backend-qc/post_install.sh`) logging to `Local/Log/celery.log`. (be careful, still uses loglevel info (might want to change this for release), so the file could get big fast). You shouldn't need to manually kill the workers with this setup, uses celery multi.
Look at `qc/scripts/*GenGraphs.py` and `qc/scripts/genGraphs.py` (parallelization) for getting the decoded graphs for the QC modules (Cleanup and Marosijo).

## Selecting modules to use

In order to decide which QC modules to use, you need to modify `config.py`, both the imports and the activeModules dict to include the QC modules you want to use.

If any modules are added/removed to/from activeModules, the `setupActiveModules.sh` script needs to be run to add them to the relevant places, which is `celery_handler.py` because celery_handler.py needs to use their BaseTask to create it's own processing task for each module.
Format of adding modules to activeModules:
  `mod=dict(name='UniqueNameModule', task='UniqueNameTask', processFn=qcProcSessionUniqueNameModule)`

For example, I have a module TestModule, which is in `TestModule.py`
Then I add `TestModule=dict(name='TestModule', task='TestTask', processFn=qcProcSessionTestModule)` to activeModules and add 
```
try:
    # you need to manually add imports here
    from .celery_handler import qcProcSessionTestModule
except SystemError:
    # and here
    qcProcSessionTestModule = None
```
at the top.

Then the script will handle adding: `from .celery_handler import qcProcSessionTestModule` and adding the template code and replacing `@celery.task(base=TestTask)` and `TestModule` with your module in `celery_handler.py`.


## Creating your own modules

To add your own QC module (lets call it New), you need to satisfy a couple of criteria

* Add a file `modules/NewModule/NewModule.py`.
* Look at e.g. `modules/TestModule/TestModule.py` for reference, but you need to create a class, NewTask, which inherits celery.Task and which will be used as a base Task for all subtasks using that QC module. This means, all subtasks have access to the data in the NewTask class (see [celery docs](http://docs.celeryproject.org/en/latest/userguide/tasks.html#custom-task-classes) for more details on this).
  * NewTask needs to be able to connect to the redis datastore, to modify the report for this QC module for each session. (with key **report/NewModule/session_id** or as specified in `redis_layout.md`) It is important that this report be JSON (double quotes people), use e.g. json.dumps before writing to redis datastore.
  * NewTask needs to define a method, processBatch which handles the processing that QC module needs to do. This method, takes as an argument a session id and indices (=[] when no new recordings are to be processed, in which case the function should return True) for recordings of that session to process in this batch (this list is stored in redis datastore by QC handler), and the task chaining which Celery uses, expects this processing function to work only on a small batch of recordings at a time (e.g. 5), so as to not take too long and be able to write intermediary results to redis to display on the client app. processBatch might take additional arguments, as specified in `modules/TestModule/TestModule.py`.
* Modify the `config.py` script, as specified in the **Selecting modules to use** section.
* Notes:
  * All files in modules/NewModule/local will be ignored by git as per .gitignore.