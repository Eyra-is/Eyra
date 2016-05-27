#!/bin/bash -eu
# Copyright 2016 Simon Klüpfel 
# Apache 2.0

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

echo "Creating directory ${YYY_WSGIROOT}"
mkdir -p ../${YYY_WSGIROOT}
sudo service apache2 reload

return 0

