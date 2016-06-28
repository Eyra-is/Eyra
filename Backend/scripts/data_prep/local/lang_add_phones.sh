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

help_message="Usage: $0 <lexiconp> <src-lang> <dst-lang>

Add phonemes as words to the dictionary of <src-lang>
"

. utils/parse_options.sh
. path.sh

sil_prob=0.5

if [ $# -ne 3 ]; then
  echo "ERROR: Expected 3 arguments (got $#)" >&2
  echo "$help_message" >&2
  exit 1
fi

lexiconp=$1
lang=$2
dstlang=$3

tmp=$(mktemp -d)

mkdir -p $dstlang


# We begin by copying the files that stay the same
#
for f in oov.int oov.txt phones.txt topo; do
  cp $lang/$f $dstlang/$f
done

mkdir -p $dstlang/phones
for f in context_indep.csl context_indep.int context_indep.txt disambig.csl \
                      disambig.int disambig.txt extra_questions.int    \
                      extra_questions.txt nonsilence.csl nonsilence.int \
                      nonsilence.txt optional_silence.csl optional_silence.int \
                      optional_silence.txt roots.int roots.txt sets.int sets.txt \
                      silence.csl silence.int silence.txt word_boundary.int \
                      word_boundary.txt; do
  cp $lang/phones/$f $dstlang/phones/$f
done

# We need lexiconp.txt
perl -ane '@A=split(" ",$_); $w = shift @A; $p = shift @A; @A>0||die;
         if(@A==1) { print "$w $p $A[0]_S\n"; } else { print "$w $p $A[0]_B "; for($n=1;$n<@A-1;$n++) { print "$A[$n]_I "; }
         print "$A[$n]_E\n"; } ' < $lexiconp > $tmp/lexiconp.pre_phones

cat $lang/phones/nonsilence.txt \
  | awk '{p=$1; gsub(/_[BEIS]/, "", p); printf "!%s %.6f %s\n", p, 1.00000, $1}' > $tmp/lexiconp.phones

cat $tmp/lexiconp.pre_phones $tmp/lexiconp.phones > $dstlang/lexiconp.txt

ndisambig=$(utils/add_lex_disambig.pl --pron-probs $dstlang/lexiconp.txt $dstlang/lexiconp_disambig.txt)

# align_lexicon
cat $dstlang/lexiconp.txt \
  | awk 'BEGIN {printf "<eps> <eps> sil\n"} {printf "%s %s ", $1, $1; for (i=3;i<=NF;i+=1){printf "%s ", $i} printf "\n"}' \
        > $dstlang/phones/align_lexicon.txt

# Add to words.txt
LC_ALL= python3 -c "
with open('$tmp/lexiconp.phones') as p, open('$lang/words.txt') as l:
  words = l.readlines()
  last_label = int(words[-1].strip().split()[-1])
  for line in words:
    print(line.strip())
  label = last_label + 1
  last_sym = ''
  sym = ' '
  for line in p:
    last_sym = sym
    sym = line.split()[0]
    if not sym == last_sym:
      print('{} {}'.format(sym, label))
      label += 1
" > $dstlang/words.txt

# int version of align_lexicon
cat $dstlang/phones/align_lexicon.txt \
  | utils/sym2int.pl -f 1-2 $dstlang/words.txt \
  | utils/sym2int.pl -f 3- $dstlang/phones.txt \
                     > $dstlang/phones/align_lexicon.int

silphone=$(cat $lang/phones/optional_silence.txt)
# Create L.fst
utils/make_lexicon_fst.pl --pron-probs $dstlang/lexiconp.txt $sil_prob $silphone | \
    fstcompile --isymbols=$dstlang/phones.txt --osymbols=$dstlang/words.txt \
    --keep_isymbols=false --keep_osymbols=false | \
     fstarcsort --sort_type=olabel > $dstlang/L.fst


# L.fst with disambiguation symbols
# add an extra special disambiguation symbol

cp $dstlang/phones.txt $tmp/phones.txt
awk '{c=$2;print} END {print "#00 " c+1}' < $tmp/phones.txt > $dstlang/phones.txt
echo '#00' >> $dstlang/phones/disambig.txt
utils/sym2int.pl $dstlang/phones.txt < $dstlang/phones/disambig.txt > $dstlang/phones/disambig.int

cp $dstlang/words.txt $tmp/words.txt
awk '{c=$2;print} END {print "#00 " c+1}' < $tmp/words.txt > $dstlang/words.txt
(echo '#0'; echo '#00' ) > $dstlang/phones/wdisambig.txt
utils/sym2int.pl $dstlang/words.txt < $dstlang/phones/wdisambig.txt > $dstlang/phones/wdisambig.int

utils/make_lexicon_fst.pl --pron-probs $dstlang/lexiconp_disambig.txt $sil_prob $silphone '#'$ndisambig | \
  fstcompile --isymbols=$dstlang/phones.txt --osymbols=$dstlang/words.txt \
             --keep_isymbols=false --keep_osymbols=false |   \
  fstaddselfloops  "grep -e '#0' -e '#00' $dstlang/phones/disambig.txt | utils/sym2int.pl $dstlang/phones.txt |" $dstlang/phones/wdisambig.int | \
  fstarcsort --sort_type=olabel > $dstlang/L_disambig.fst

awk 'END {printf "$LMLM %d", NR}' < $dstlang/words.txt >> $dstlang/words.txt
