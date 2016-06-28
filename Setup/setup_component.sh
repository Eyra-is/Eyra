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

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

[[ "$#" == "1" ]] || {
  echo "$0: This script needs exactly one argument!"
  exit 1
}

SRCDIR=$( realpath -s $1 )
TNAME=$( basename ${SRCDIR} )

BDIR=$( dirname $( realpath -s ${BASH_SOURCE[0]} ) )

# get dependencies
bash ${BDIR}/install_dependencies.sh ${SRCDIR} || err

SEDF=${TNAME}.sed

# preparing the sed script
[[ -f ${SRCDIR}/default.conf ]] && {
cut -d "=" -f 1 ${SRCDIR}/default.conf | \
  grep -v -e "^#" | grep -v -e "^ *$" | \
  while read var; do
    if [[ "${var:0:4}" == "YYY_" ]]; then
      repdir="${BDIR}/../${!var}"
      mkdir -p "$repdir"
      echo "s|XXX${var:4}XXX|$(realpath -s $repdir)|"
    else
      echo "s|XXX${var}XXX|${!var}|"
    fi
  done > ${SEDF}
} || {
  : > ${SEDF}
}

echo "s|XXXUSERXXX|$USER|" >> ${SEDF}
echo "s|XXXGROUPXXX|$USER|" >> ${SEDF}

# Files to be installed globally
[[ -e ${SRCDIR}/global.files ]] && \
for f in $( cat ${SRCDIR}/global.files ); do 
  OUTF=Root${f}
  RSTR=${f//\//_}
  INF=${SRCDIR}/tmpl/${RSTR:1}
  parse_file $INF $OUTF $SEDF
echo $INF $OUTF $SEDF
done

# Globally installed files to be modified
[[ -e ${SRCDIR}/global.mod.files ]] && \
cat ${SRCDIR}/global.mod.files | while read line; do 
  F=( $line )
  FILE="${F[0]}"
  COMS="${F[@]:1}"
  if [[ ! -z "$COMS" ]]; then
    eval $COMS > Root${FILE}
  fi
done

[[ -e ${SRCDIR}/local.files ]] && \
for f in $( cat ${SRCDIR}/local.files ); do 
  OUTF=${f:1}
  RSTR=${f//\//_}
  INF=${SRCDIR}/tmpl/${RSTR:1}
  parse_file $INF $OUTF $SEDF
done

return 0
