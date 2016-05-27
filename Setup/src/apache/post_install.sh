#!/bin/bash -eu
# Copyright 2016 Simon Klüpfel 
# Apache 2.0

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}


report "Setting Up Apache ..."

mkdir -p etc/apache2/vhosts/

for i in $(ls -1 /etc/apache2/sites-available/); do
  sudo a2dissite ${i} 
done && \
sudo a2ensite datatool.conf && \
sudo a2dismod mpm_prefork mpm_event && \
sudo a2enmod ssl wsgi mpm_worker rewrite && \
sudo service apache2 restart && suc || err

return
