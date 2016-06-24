#!/bin/bash -eu
#
# Copyright 2016 Simon Klüpfel, Róbert Kjaran
# Apache 2.0

extra_disambig_sym="#00"
nonfincost=$(echo "-l(1/3)" | bc -l)
epscost=$nonfincost
lmcost=$nonfincost
wcost=$nonfincost
silcost=$nonfincost
finalcost=$(echo "-l(1/2)" | bc -l)
lmlabel=\$LMLM
sillabel="!sil"

help_message='Usage: '$0' <lm-fst> <symtab> < utts.txt > utt-fsts.ark

Creates one decoding graph per utterance.

G FST where P (i.e. <lm-fst>) is a phoneme bigram model and wi is the word sequence:
    _eps_   _eps_   _eps_   _eps_
   / w1  \ /  w2 \ /  w3 \ /  w4 \
 (1)---->(2)---->(3)---->(4)---->(5)
/   \   /   \   /   \   /   \   /   \
\_P_/   \_P_/   \_P_/   \_P_/   \_P_/

'

make_determinable () {
  fstprint -{i,o}symbols=$symtab \
    | perl -ape 's:^(\d+\s+\d+\s+)\<eps\>(\s+):$1'$extra_disambig_sym'$2:;' \
    | fstcompile -{i,o}symbols=$symtab \
    | fstdeterminize | fstminimize | fstarcsort --sort_type=ilabel
}

if [ "${1:-}" == "--help" -o "${1:-}" == "-h" -o $# -ne 2 ]; then
  echo "$help_message" >&2
  exit 1
fi

lmfst=$1
symtab=$2


while read line; do
  words=( $line )
  label=${words[0]}
  echo $label
  words=(${words[@]:1})


  lmind=$(grep -w "$lmlabel" "$symtab" | awk '{print $2}')

  if [ -z "$lmind" ]; then
    echo >&2
    echo "ERROR: Could not find $lmlabel in $symtab." >&2
    echo "Did you forget to run lang_add_phones.sh?" >&2
    echo "Or did you use the wrong lang folder?" >&2
    exit 1
  fi

  fstreplace \
    --epsilon_on_replace <( (
                            ind=0
                            for w in ${words[@]}; do
                              echo "$ind $ind $lmind $lmind $lmcost"
                              echo "$ind $(( $ind + 1 )) $w $w $wcost"
                              echo "$ind $(( $ind + 1 )) 0 0 $epscost"
                              ind=$(( $ind + 1 ))
                            done
                            echo "$ind $ind $lmind $lmind $finalcost"
                            echo "$ind $finalcost"
                          ) | fstcompile
                          ) -1 $lmfst $lmind \
                            | make_determinable | fstprint

  echo
done

