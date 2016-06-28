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
#     Róbert Kjaran <robert@kjaran.com>
#     Matthias Petursson <oldschool01123@gmail.com> (work for session files named 5 or session_5)

help_message="Usage: $0 <path-to-qc-report-dumps>
Grabs the newest line from the session dumps. Only works for the Marosijo module."

if [ $# -ne 1 -o "$1" = "--help" -o "$1" = "-h" ]; then
  echo "$help_message" >&2
  exit 1
fi
qc_path=$1

echo -e "# sessionId\ttokenId\taccuracy\tonlyInsOrSub\tcorrect\tsub\tins\tdel\tstartdel\tenddel\textraInsertions\tempty\tdistance"
for session in $qc_path/*; do
  session_id=$(echo "$session" | sed "s:$qc_path/::" | sed "s:session_::")
  jq --arg session_id "$session_id" -r '.perRecordingStats[] | [($session_id|tonumber), .recordingId, .stats.accuracy, .stats.onlyInsOrSub, .stats.correct, .stats.sub, .stats.ins, .stats.del, .stats.startdel, .stats.enddel, .stats.extraInsertions, .stats.empty, .stats.distance] | @csv' \
    < $session | tr ',' '\t'
done
