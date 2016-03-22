# Generic config file for all QC.
# QC runs all the modules specified in the activeModules dict.
#   the keys in said dict should be a string representation
#   of the module names, as found in type(module).__name__

# IMPORTANT NOTICE
# READ THIS
# If any modules are added to activeModules, a script needs to be run
#   to add them to the relevant places, which are this file and celery_handler.py
#   because celery_handler.py needs to use their BaseTask to create it's own
#   processing task for each module, and config.py needs to add the relative imports
#   of the processing functions.
#   Format of adding modules to activeModules:
#   mod=dict(name='UniqueNameModule', processFn=qcProcSessionUniqueNameModule)
#
# For example, I have a module TestModule, which is in TestModule.py
# Then I add 'TestModule=dict(name='TestModule', processFn=qcProcSessionTestModule)
#   and the script will handle adding: from .celery_handler import qcProcSessionTestModule
#   and adding @celery.task(base=TestTask) in celery_handler.py

# this code is generated from script
# @@CELERYQCMODULEIMPORTS
from .celery_handler import qcProcSessionTestModule
# @@/CELERYQCMODULEIMPORTS

activeModules = dict(
    TestModule=dict(name='TestModule', processFn=qcProcSessionTestModule)
)

# default to no processing
if len(activeModules) == 0:
    from .celery_handler import qcProcSessionDummyModule
    activeModules = dict(
        DummyModule=dict(name='DummyModule', processFn=qcProcSessionDummyModule)
    )
