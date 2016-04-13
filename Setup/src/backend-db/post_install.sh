#!/bin/bash -eu

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

# recordings are saved in /data/eyra, need to make sure our server
#   has permissions to write there.
if [ ! -d "/data" ]; then 
    sudo mkdir "/data" 
fi
if [ ! -d "/data/eyra" ]; then 
    sudo mkdir "/data/eyra" 
fi
sudo chown $USER "/data/eyra"

sudo service apache2 reload

return 0

