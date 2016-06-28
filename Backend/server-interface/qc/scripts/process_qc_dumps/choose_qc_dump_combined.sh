#!/bin/bash -ue
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

help_message="Usage: $0 <qc-report-dump-combined> <#recs> <from-month> [<to-month>]"

if [ $# -le 3 -a $# -ge 4 -o "${1:-}" = "--help" -o "${1:-}" = "-h" ]; then
  echo "Got $# args" >&2
  echo "$help_message" >&2
  exit 1
fi
in_dump=$1
n_recs=$2
from_month=$3
to_month=${4:-$(date +%m)}

month_filter() {
  # filename field (15) contains timestamp in ISO format
  # example Lisa12_2016-05-02T09:03:59.722Z.wav
  awk -F'\t' -vfrom_month=$from_month -vto_month=$to_month 'match($15, /20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]/) { d=substr($15, RSTART, RLENGTH); split(d, A, "-"); if(A[2]>=from_month && A[2] <= to_month) print; } '
}

choose() {
  shuf -n $n_recs
}

head -n 1 < $in_dump

tail -n +2 $in_dump \
  | month_filter \
  | choose

