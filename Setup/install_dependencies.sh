#!/bin/bash -eu

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
  sudo aptitude -q2 update && \
  sudo aptitude -y install $(cat ${1}/aptitude.deps) && 
  suc || err
}

[[ -e  ${1}/pip3.deps ]] && [[ ! -z  "$( cat ${1}/pip3.deps )" ]] && {
  report "Installing dependencies (pip3) " && \
  sudo pip3 install $(cat ${1}/pip3.deps) && \
  suc || err
}

exit 0
