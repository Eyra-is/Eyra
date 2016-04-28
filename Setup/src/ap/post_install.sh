#!/bin/bash -eu

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

chmod 755 ./bin/restart_wifi_ap.sh
chmod 755 ./bin/restart_wifi_client.sh

sudo ./bin/restart_wifi_ap.sh

report "WiFi Status:"
sudo iw $WIFI_DEV info

return 0
