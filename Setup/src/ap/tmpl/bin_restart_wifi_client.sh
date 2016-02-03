#!/bin/bash

if [ "$(id -u)" != "0" ]; then
   echo "This script has to be run as root." 1>&2
   exit 1
fi

service dnsmasq stop
service hostapd stop
service network-manager stop
[[ -e /etc/network/interfaces.d/wlan0.conf ]] && mv /etc/network/interfaces.d/wlan0.conf{,_}
service networking restart
service network-manager start

