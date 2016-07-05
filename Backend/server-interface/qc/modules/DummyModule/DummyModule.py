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

import redis

# grab celery_config from dir above this one
# thanks, Alex Martelli, http://stackoverflow.com/a/1054293/5272567
import sys
import os.path
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(newPath)
import celery_config
sys.path.remove(newPath)
del newPath

from celery import Task

class DummyTask(Task):
    """DummyTask - Do no quality control
    """
    abstract = True
    _redis = None

    @property
    def redis(self):
        if self._redis is None:
            self._redis = redis.StrictRedis(
                host=celery_config.const['host'], 
                port=celery_config.const['port'], 
                db=celery_config.const['backend_db'])

        return self._redis

    def processBatch(self, name, session_id, indices) -> bool:
        """
        Dummy method, always sets same report in redis datastore, i.e.
            {"totalStats": {"accuracy":0},
             "report" : "No report (dummy)."}
            with key: report/name/session_id
        """
        self.redis.set('report/{}/{}'.format(name, session_id), 
                        {"totalStats": {"accuracy":0},
                         "report" : "No report (dummy)."})
        return False