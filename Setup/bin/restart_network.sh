#!/bin/bash

service dnsmasq stop
service hostapd stop
service network-manager stop
service networking restart
service network-manager start
service hostapd start
service dnsmasq start

