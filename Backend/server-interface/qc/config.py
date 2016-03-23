# Generic config file for all QC.
# QC runs all the modules specified in the activeModules dict.
#   the keys in said dict should be a string representation
#   of the module names, as found in type(module).__name__

# IMPORTANT NOTICE
# READ THIS
# If any modules are added to activeModules, the setupActiveModules.sh script needs to be run
#   to add them to the relevant places, which is celery_handler.py
#   because celery_handler.py needs to use their BaseTask to create it's own
#   processing task for each module.
#   Format of adding modules to activeModules:
#   mod=dict(name='UniqueNameModule', task='UniqueNameTask', processFn=qcProcSessionUniqueNameModule)
#
# For example, I have a module TestModule, which is in TestModule.py
# Then I add 'TestModule=dict(name='TestModule', task='TestTask', processFn=qcProcSessionTestModule)'
#   and the script will handle adding: from .celery_handler import qcProcSessionTestModule
#   and adding @celery.task(base=TestTask) in celery_handler.py

# this try block is because when importing this file
# in the setupActiveModules.py script, it did not work.
# and in that script we only need name and task for the modules
# so in that case we can ignore the actual functions in the modules
try:
    # you need to manually add imports here
    from .celery_handler import qcProcSessionTestModule
    #from .celery_handler import qcProcSessionDummyModule
except SystemError:
    # and here
    qcProcSessionTestModule = None
    #qcProcSessionDummyModule = None

activeModules = dict(
    TestModule=dict(
        name='TestModule', 
        task='TestTask', 
        processFn=qcProcSessionTestModule),
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
