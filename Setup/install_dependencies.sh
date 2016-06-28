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

[[ "${BASH_SOURCE[0]}" == "${0}" ]] || {
  echo "$0: This script should be executed, not sourced!"
  exit 1
}

[[ "$#" == "1" ]] || {
  echo "$0: This script needs exactly one argument!"
  exit 1
}

# load helper functions
. $( dirname $( readlink -f $0 ) )/fn_report.sh

[[ -e  ${1}/aptitude.deps ]] && [[ ! -z  "$( cat ${1}/aptitude.deps )" ]] && {
  report "Installing dependencies (aptitude) " && \
  sudo apt-get -q2 update && \
  sudo apt-get -y install $(cat ${1}/aptitude.deps) && 
  suc || err
}

[[ -e  ${1}/pip3.deps ]] && [[ ! -z  "$( cat ${1}/pip3.deps )" ]] && {
  report "Installing dependencies (pip3) " && \
  sudo pip3 install $(cat ${1}/pip3.deps) && \
  suc || err
}

[[ -e  ${1}/custom.deps.sh ]] &&  {
  report "Installing dependencies (custom) " && \
  bash ${1}/custom.deps.sh && \
  suc || err
}

exit 0
