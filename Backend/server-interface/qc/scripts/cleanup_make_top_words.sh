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

../../../scripts/data_prep/utils/sym2int.pl --map-oov "<UNK>" ../modules/CleanupModule/data/words.syms <(cut -d' ' -f 2- jv_toks | tr '[:upper:]' '[:lower:]') | awk 'BEGIN{total=0;}{a[$1]++; total++;}END{for(k in a)printf "%.5f %d\n", a[k]/total,k}' RS=" |\n" | sort -n -r | head -101 | tail -n 100 > ../modules/CleanupModule/data/top_words.int
