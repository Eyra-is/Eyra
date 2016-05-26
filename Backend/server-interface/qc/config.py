# Generic config file for all QC.
# QC runs all the modules specified in the activeModules dict. 
#   More info in README.md in qc directory.

# this try block is because when importing this file
# in the setupActiveModules.py script, it did not work.
# and in that script we only need name and task for the modules
# so in that case we can ignore the actual functions in the modules
try:
    # you need to manually add imports here
    #from .celery_handler import qcProcSessionCleanupModule
    from .celery_handler import qcProcSessionMarosijoModule
    #from .celery_handler import qcProcSessionTestModule
    #from .celery_handler import qcProcSessionDummyModule
except SystemError:
    # and here
    qcProcSessionCleanupModule = None
    qcProcSessionMarosijoModule = None
    #qcProcSessionTestModule = None
    #qcProcSessionDummyModule = None

activeModules = dict(
    MarosijoModule=dict(
        name='MarosijoModule',
        task='MarosijoTask',
        processFn=qcProcSessionMarosijoModule),
    # CleanupModule=dict(
    #    name='CleanupModule', 
    #    task='CleanupTask', 
    #    processFn=qcProcSessionCleanupModule),
    # TestModule=dict(
    #     name='TestModule', 
    #     task='TestTask', 
    #     processFn=qcProcSessionTestModule),
    # DummyModule=dict(
    #     name='DummyModule', 
    #     task='DummyTask', 
    #     processFn=qcProcSessionDummyModule)
)



# default to no processing
if len(activeModules) == 0:
    try:
        from .celery_handler import qcProcSessionDummyModule
    except SystemError:
        qcProcSessionDummyModule = None
    activeModules = dict(
        DummyModule=dict(name='DummyModule', task='DummyTask', processFn=qcProcSessionDummyModule)
    )
