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
#     Matthias Petursson <oldschool01123@gmail.com>

# Looks at the agreement in $agreementPath and updates table recording_agreement in accordance.
# Loses newline information in the transfer (changes newlines to a space)

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

agreementPath="../Frontend/da-webapp/src/views/recording-agreement.html"

# Usage: update_id oldId newId
update_id() {
    echo "Modifying file $agreementPath with updated id."
    sed -i 's/agreement-id="'$1'/agreement-id="'$2'/' "$agreementPath"
}

report "Getting current agreement from $agreementPath"
agreement="$(cat "$agreementPath" | \
  tr '\n' ' ' | \
  sed -n 's:.*<!--\s*start\s*agreement\s*-->\(.*\)<!--\s*end\s*agreement\s*-->.*:\1:p')"

# Checking if that agreement is already in database
dbAgreementId="$(mysql -u root -p -D recordings_master -e "select id from recording_agreement where agreement='$agreement'" | tail -1)"

# thank you Mark Byers! http://stackoverflow.com/a/3027524/5272567
agreementId="$(grep -oP "agreement-id=\".*?\"" "$agreementPath" | \
               sed 's/agreement-id="//' | sed 's/"//')"

if [ "$dbAgreementId" ]; then
    report "Agreement in database."
    report "Making sure ids match."
    if [ "$agreementId" = "$dbAgreementId" ]; then
        report "Ids match!"
    else
        report "Ids don't match."
        update_id "$agreementId" "$dbAgreementId"
    fi
else
    report "Agreement not in database."
    report "Copying current agreement and inserting into database."
    mysql -u root -p -D recordings_master -e "insert into recording_agreement (agreement) values ('$agreement')"
    report "Grabbing agreement id."
    dbAgreementId="$(mysql -u root -p -D recordings_master -e "select id from recording_agreement where agreement='$agreement'" | tail -1)"
    update_id "$agreementId" "$dbAgreementId"
fi

return 0
