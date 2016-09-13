#!/bin/bash
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
#     Matthias Petursson <oldschool01123@gmail.com>

# Create a confusion table from Marosijo analized vs dump from evaluation from database


display_usage() { 
    echo 
"Usage: $0 data_file accuracy_column grade_column
Outputs a confusion table pairing Marosijo accuracies (0-1) with manual grades (0-4)
done through the evaluation feature in Eyra.
Parameters:
    data_file           the file with the parsed dump joined on recId with sql dump from evaluation
    accuracy_column     which column the marosijo accuracy is in.
    grade_column        which column the evaluation grades are in.

Example:
    ./$0 qc_dump_plus_grades.tsv 4 22
" >&2
} 
if [[ ( $1 == "--help") ||  $1 == "-h" ]] 
then 
    display_usage
    exit 0
fi 
if [[ "$#" -ne 3 ]]; then
    display_usage
    exit 1
fi

data_file=$1
acc_col=$2
grade_col=$3

res=$(awk -F $'\t' -v acc_col="$acc_col" -v grade_col="$grade_col" \
      '{tot[$grade_col]++; \
        if ($acc_col == 1) { one[$grade_col]++; } \
        if ($acc_col >0 && $acc_col <1) { med[$grade_col]++; } \
        if ($acc_col == 0) { zero[$grade_col]++; } \
        if ($acc_col >= 0.8) { over08[$grade_col]++; } \
        if ($acc_col >= 0.7) { over07[$grade_col]++; } \
        if ($acc_col >= 0.5 && $acc_col < 0.7) { over05less07[$grade_col]++; } \
        if ($acc_col >= 0.2 && $acc_col < 0.5) { over02less05[$grade_col]++; } \
        if ($acc_col < 0.2) { less02[$grade_col]++; } \
       } \
       END{ for (grade in tot) { \
                printf "%s\t\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n", grade, one[grade], med[grade], zero[grade], tot[grade], \
                        over08[grade], over07[grade], over05less07[grade], over02less05[grade], less02[grade]; \
            } \
            printf "in %\n"; \
            for (grade in tot) { \
                printf "%s\t\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n", grade, one[grade]*100/tot[grade], med[grade]*100/tot[grade], zero[grade]*100/tot[grade], tot[grade]*100/tot[grade], \
                        over08[grade]*100/tot[grade], over07[grade]*100/tot[grade], over05less07[grade]*100/tot[grade], over02less05[grade]*100/tot[grade], less02[grade]*100/tot[grade]; \
            } }' \
       $data_file)

echo -e "Grade/accuracy\t1\t<1\t0\ttotal\tover 0.8\tover 0.7\t0.5<=x<0.7\t0.2<=x<0.5\tless 0.2"
echo "$res"