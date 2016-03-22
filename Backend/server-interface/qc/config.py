# Generic config file for all QC.
# QC runs all the modules specified in the activeModules dict.
#   the keys in said dict should be a string representation
#   of the module names, as found in type(module).__name__

from .modules.dummy import DummyModule
from .modules.test import TestModule

activeModules = dict(
    DummyModule=DummyModule,
    TestModule=TestModule
)

# default to no processing
if len(activeModules) == 0:
    activeModules = dict(DummyModule=DummyModule)
