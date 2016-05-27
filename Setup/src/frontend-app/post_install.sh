#!/bin/bash -eu
# Copyright 2016 Simon Klüpfel 
# Apache 2.0

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

TDIR=$(pwd)
cd ../${YYY_SITEROOT}/..
report "Running npm install"
npm install && suc || err
report "Running grunt deploy"
./node_modules/grunt-cli/bin/grunt deploy  && suc || err
cd ${TDIR}

sudo service apache2 reload

return 0

