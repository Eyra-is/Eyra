#!/bin/bash -eu
#

help_message="Usage: $0 <ali-dir> <lang-dir> <out-fst>

Create phone bigram FST from alignments.
"

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
  | awk '{printf "%s ", $1; for(i=2; i<=NF; i+=1) { if($i!="sil" && $i !~ /^spn_[BEIS]/) {printf "!%s ", gensub(/_[BEIS]/, "", "g", $i) } } printf "\n" }' \
  | utils/sym2int.pl -f 2- $lang/words.txt \
  | chain-est-phone-lm --num-extra-lm-states=0 --ngram-order=2 --no-prune-ngram-order=2 ark:- $out
