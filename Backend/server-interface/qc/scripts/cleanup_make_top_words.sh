# Copyright 2016 Matthias Petursson
# Apache 2.0

../../../scripts/data_prep/utils/sym2int.pl --map-oov "<UNK>" ../modules/CleanupModule/data/words.syms <(cut -d' ' -f 2- jv_toks | tr '[:upper:]' '[:lower:]') | awk 'BEGIN{total=0;}{a[$1]++; total++;}END{for(k in a)printf "%.5f %d\n", a[k]/total,k}' RS=" |\n" | sort -n -r | head -101 | tail -n 100 > ../modules/CleanupModule/data/top_words.int
