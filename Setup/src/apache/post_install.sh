#!/bin/bash -eu
#
# Copyright 2016 The Eyra Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File author/s:
#     Simon Klüpfel 

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

report "Setting Up Apache ..."

mkdir -p etc/apache2/vhosts/

if [ ! -f etc/apache2/server-status_htpasswd ]; then
    report "Provide password for /diagnostics-status (server-status)"
    report "Username will be 'admin'"
    htpasswd -c etc/apache2/server-status_htpasswd admin
fi

for i in $(ls -1 /etc/apache2/sites-available/); do
  sudo a2dissite ${i} 
done && \
sudo a2ensite datatool.conf && \
sudo a2dismod mpm_prefork mpm_event && \
sudo a2enmod ssl wsgi mpm_worker rewrite status && \
sudo service apache2 restart && suc || err

return
