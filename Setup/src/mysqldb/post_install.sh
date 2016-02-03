#!/bin/bash -eu

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

# At this point we are working in Local/
../Backend/db/erase_and_rewind.sh

return 0
