#!/bin/bash -eu
# Copyright 2016 Simon Klüpfel 
# Apache 2.0

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
