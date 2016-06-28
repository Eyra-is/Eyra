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

const = dict(
    # redis vars
    host = 'localhost',
    port = 6379,
    broker_db = 0,
    backend_db = 1,
    #
    session_timeout = 240,#15*60, # timeout in seconds, assume session is over, if 15 mins have passed since last query for report 
    task_min_proc_time = 200000, # minimum time (in microseconds) a processing function should take as to not invoke delays to not put tasks in rapid succession on the queue
    task_delay = 0.2, # time (in seconds) a process is set to sleep in the event of task taking less than task_min_proc_time
    batch_size = 600, # number of recordings to process at a time (per task)
    qc_report_dump_path = '/data/eyra/qc_reports',
    qc_offline_mode = True,
    qc_big_batch_mode = True
)
