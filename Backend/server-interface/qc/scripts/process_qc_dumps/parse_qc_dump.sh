#!/bin/bash -eu
# Copyright: 2016 Robert Kjaran <robert@kjaran.com>
#            2016 Matthias Petursson (work for session files named 5 or session_5)
# Apache 2.0
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
