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
#     Simon Klüpfel <simon.kluepfel@gmail.com>
#     Matthias Petursson <oldschool01123@gmail.com>

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

echo "Are you sure you want to run --mysqldb, it will delete the entire mysql database? Note you can run './setup.sh --all --no-mysqldb' to avoid this. (type 1 or 2)"
select yn in "Yes" "No"; do
    case $yn in
        # At this point we are working in Local/
        Yes ) ../Backend/db/erase_and_rewind.sh; break;;
        No ) break;;
    esac
done

return 0
