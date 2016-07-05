# Copyright 2016 The Eyra Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File author/s:
#     Matthias Petursson <oldschool01123@gmail.com>

# Generic config file for all QC.
# QC runs all the modules specified in the activeModules dict. 
#   More info in DEVELOPER.md in project root directory.

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
    #qcProcSessionCleanupModule = None
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
