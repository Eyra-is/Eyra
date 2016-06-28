#!/bin/bash -eu
#
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
#     Simon Klüpfel
#     Matthias Petursson <oldschool01123@gmail.com>

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

report "Firing up Celery worker for QC.. log in Local/Log/celery.log"
cd ../Backend/server-interface
# if we have more than 1 thread, set celery to use all except 1
nproc=$(nproc)
if [ $nproc -ne 1 ]; then
    nproc=$[nproc - 1]
else
    report_err "Using QC with only 1 thread is BAD. Get more cores pls."
fi
celery multi restart 1 -A qc.celery_handler.celery -c $nproc -D -f ../../Local/Log/celery.log --loglevel=info
cd -

return
