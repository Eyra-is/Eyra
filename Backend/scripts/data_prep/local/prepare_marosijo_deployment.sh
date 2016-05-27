#!/bin/bash -eu
# Copyright:  2016  Robert Kjaran <robert@kjaran.com>
# Apache 2.0
#
# Prepares a tarball with files necessary for the Marosijo QC module
# in Eyra

help_message="Usage: $0 <lang-dir> <exp-dir> <phone-lm-fst> <sample-freq> <out-tgz>"

err() {
  msg=$1
  code=${2:-1}
  echo "$msg" >&2
  exit $code
}

msg() {
  echo "$1" >&2
}

if [ $# -ne 5 ]; then
  err "$help_message"
fi

lang=$1
exp=$2
phone_lm_fst=$3
sample_freq=$4
out_tgz=$5

tmp="$(mktemp -d)"
trap "rm -rf $tmp" EXIT


msg "Copying files from $lang"
cp $lang/L_disambig.fst $tmp/lexicon_fst \
  || err "Lexicon FST missing from $lang"
cp $lang/oov.int $tmp/oov_int \
  || err "oov.int missing from $lang"
cp $lang/words.txt $tmp/symbol_tbl \
  || err "words.txt missing from $lang"
cp $lang/phones/disambig.int $tmp/disambig_int \
  || err "phones/disambig.int missing from $lang"

msg "Copying files from $exp"
cp $exp/tree $tmp/tree || err "tree missing from $exp"
cp $exp/final.mdl $tmp/acoustic_mdl || err "final.mdl missing from $exp"

msg "Sample frequency of WAV files is $sample_freq"
echo "$sample_freq" > $tmp/sample_freq

msg "Using Phoneme LM from $phone_lm_fst"
cp $phone_lm_fst $tmp/phone_lm || err "$phone_lm_fst missing"

tar --transform 's/.*\///g' -cvzf $out_tgz $tmp/*

msg "Done."
msg "Output in $out_tgz"
