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

display_usage() { 
    echo 
"Usage: $0 data_file accuracy_column grade_column
Outputs a confusion table with different thresholds for Marosijo accuracies (0-1) 
comparing with manual grades (0-4) done through the evaluation feature in Eyra.
Parameters:
    data_file           the file with the parsed dump joined on recId with sql dump from evaluation
    accuracy_column     which column the marosijo accuracy is in.
    grade_column        which column the evaluation grades are in.

Recommended pasting the output into some table data visualizor e.g. Google sheets.

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
        if ($grade_col == 1 || $grade_col == 2) { tot["bad"]++; } \
        if ($grade_col == 3 || $grade_col == 4) { tot["good"]++; } \
        if ($acc_col >= 1.0) { over10[$grade_col]++; \
            if ($grade_col == 1 || $grade_col == 2) { over10["bad"]++; } \
            if ($grade_col == 3 || $grade_col == 4) { over10["good"]++; } } \
        if ($acc_col >= 0.9) { over09[$grade_col]++; \
            if ($grade_col == 1 || $grade_col == 2) { over09["bad"]++; } \
            if ($grade_col == 3 || $grade_col == 4) { over09["good"]++; } } \
        if ($acc_col >= 0.8) { over08[$grade_col]++; \
            if ($grade_col == 1 || $grade_col == 2) { over08["bad"]++; } \
            if ($grade_col == 3 || $grade_col == 4) { over08["good"]++; } } \
        if ($acc_col >= 0.7) { over07[$grade_col]++; \
            if ($grade_col == 1 || $grade_col == 2) { over07["bad"]++; } \
            if ($grade_col == 3 || $grade_col == 4) { over07["good"]++; } } \
        if ($acc_col >= 0.6) { over06[$grade_col]++; \
            if ($grade_col == 1 || $grade_col == 2) { over06["bad"]++; } \
            if ($grade_col == 3 || $grade_col == 4) { over06["good"]++; } } \
        if ($acc_col >= 0.5) { over05[$grade_col]++; \
            if ($grade_col == 1 || $grade_col == 2) { over05["bad"]++; } \
            if ($grade_col == 3 || $grade_col == 4) { over05["good"]++; } } \
        if ($acc_col >= 0.4) { over04[$grade_col]++; \
            if ($grade_col == 1 || $grade_col == 2) { over04["bad"]++; } \
            if ($grade_col == 3 || $grade_col == 4) { over04["good"]++; } } \
        if ($acc_col >= 0.3) { over03[$grade_col]++; \
            if ($grade_col == 1 || $grade_col == 2) { over03["bad"]++; } \
            if ($grade_col == 3 || $grade_col == 4) { over03["good"]++; } } \
        if ($acc_col >= 0.2) { over02[$grade_col]++; \
            if ($grade_col == 1 || $grade_col == 2) { over02["bad"]++; } \
            if ($grade_col == 3 || $grade_col == 4) { over02["good"]++; } } \
        if ($acc_col >= 0.1) { over01[$grade_col]++; \
            if ($grade_col == 1 || $grade_col == 2) { over01["bad"]++; } \
            if ($grade_col == 3 || $grade_col == 4) { over01["good"]++; } } \
        if ($acc_col >= 0.0) { over00[$grade_col]++; \
            if ($grade_col == 1 || $grade_col == 2) { over00["bad"]++; } \
            if ($grade_col == 3 || $grade_col == 4) { over00["good"]++; } } \
       } \
       END{ for (grade in tot) { \
                printf "%s\t%s\t\t", grade, tot[grade]; \
                printf "%s\t%s\t\t", over10[grade], tot[grade] - over10[grade]; \
                printf "%s\t%s\t\t", over09[grade], tot[grade] - over09[grade]; \
                printf "%s\t%s\t\t", over08[grade], tot[grade] - over08[grade]; \
                printf "%s\t%s\t\t", over07[grade], tot[grade] - over07[grade]; \
                printf "%s\t%s\t\t", over06[grade], tot[grade] - over06[grade]; \
                printf "%s\t%s\t\t", over05[grade], tot[grade] - over05[grade]; \
                printf "%s\t%s\t\t", over04[grade], tot[grade] - over04[grade]; \
                printf "%s\t%s\t\t", over03[grade], tot[grade] - over03[grade]; \
                printf "%s\t%s\t\t", over02[grade], tot[grade] - over02[grade]; \
                printf "%s\t%s\t\t", over01[grade], tot[grade] - over01[grade]; \
                printf "%s\t%s\t\t",   over00[grade], tot[grade] - over00[grade]; \
                printf "\n"; \
            } }' \
       $data_file)

echo -n -e "gr/acc\ttotal\t"
for i in $(seq 1 -0.1 0); do 
    echo -n -e "$i\tgood\tbad\t"
done 
echo
echo "$res"