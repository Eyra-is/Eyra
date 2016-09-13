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

help_message="Usage: $0 <ali-dir> <lang-dir> <out-fst>

Create phone bigram FST from alignments.
"

. ./path.sh

if [ $# -ne 3 ]; then
  echo "$help_message" >&2
  exit 1
fi

ali=$1
lang=$2
out=$3

nj=$(cat $ali/num_jobs)

gunzip -c $(for n in $(seq 1 $nj); do echo $ali/ali.$n.gz; done) \
  | ali-to-phones $ali/final.mdl ark:- ark,t:- \
  | utils/int2sym.pl -f 2- $lang/phones.txt \
  | awk '{printf "%s ", $1; for(i=2; i<=NF; i+=1) { if($i!="sil" && $i !~ /^spn_[BEIS]/) {gsub(/_[BEIS]/, "", $i); printf "!%s ", $i } } printf "\n" }' \
  | grep -vE "[0-9-]+ $" \
  | utils/sym2int.pl -f 2- $lang/words.txt \
  | chain-est-phone-lm --num-extra-lm-states=1000 --ngram-order=2 --no-prune-ngram-order=1 ark:- $out
