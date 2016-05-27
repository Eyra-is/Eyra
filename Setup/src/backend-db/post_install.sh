#!/bin/bash -eu
# Copyright 2016 Simon Klüpfel 
#                Matthias Petursson
# Apache 2.0

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

# recordings are saved in /data/eyra, need to make sure our server
#   has permissions to write there.
if [ ! -d "/data" ]; then 
    report "/data doesn't exist, creating"
    sudo mkdir "/data" 
fi
if [ ! -d "/data/eyra" ]; then 
    report "/data/eyra doesn't exist, creating"
    sudo mkdir "/data/eyra" 
fi
report "Giving permissions to user '$USER' for /data/eyra"
sudo chown $USER "/data/eyra"

sudo service apache2 reload

return 0

