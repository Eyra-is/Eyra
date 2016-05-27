#!/bin/bash -eu
# Copyright 2016 Simon Klüpfel 
#                Matthias Petursson
# Apache 2.0

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
