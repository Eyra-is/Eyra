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

[[ "$#" == "3" ]] || {
  echo "$0: This script needs exactly three arguments!"
  exit 1
}

FLIST=$1
SDIR=$2
BDIR=$3

[[ -f ${FLIST} ]] || {
  report_err "Can not read file list ${FLIST}"
  exit 1
}

[[ -d ${SDIR} ]] || {
  report_err "Source directory '${SDIR}' does not exist."
  exit 1
}

# load helper functions
. $( dirname $( readlink -f $0 ) )/fn_report.sh

report "Backing up and installing files ... ";
mkdir -p ${BDIR}/ || err
NBAK=$( ls -1d ${BDIR}/*/ | wc -l )
report "Found $NBAK backup(s) at ${BDIR}."

mkdir -p ${BDIR}/${NBAK} || err

for f in $( cat ${FLIST} ); do 
  echo sudo cp ${SDIR}$f $f
  if [[ -e $f ]] ; then
    mkdir -p ${BDIR}/${NBAK}/$( dirname $f )
    cp $f ${BDIR}/${NBAK}/$f
  fi
  sudo mkdir -p $( dirname $f )
  sudo cp ${SDIR}$f $f
done && suc || err

if [ $NBAK -ge 1 ]; then
  if diff -r ${BDIR}/${NBAK} ${BDIR}/$(( ${NBAK} - 1 )) > /dev/null ; then
    report_nnl "Last Config unchanged. Reverting backup ... "
    rm -r ${BDIR}/${NBAK} && suc || err
  fi
fi

exit 0
