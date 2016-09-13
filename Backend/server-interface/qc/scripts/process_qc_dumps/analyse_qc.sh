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

# Outputs some statistical info about a parsed QC dump.

display_usage() { 
    echo 
"Usage: $0 data_file accuracy_column
Outputs some statistical info about a parsed QC dump.
Parameters:
    data_file           the file with the parsed dump
    accuracy_column     which column the marosijo accuracy is in.

Example:
    ./$0 qc_dump_combined.txt 3
" >&2
} 
if [[ ( $1 == "--help") ||  $1 == "-h" ]] 
then 
    display_usage
    exit 0
fi 
if [[ "$#" -lt 2 || "$#" -gt 2 ]]; then
    display_usage
    exit 1
fi

data_file=$1
acc_col=$2

tot=$(awk -v acc_col="$acc_col" -v data_file="$data_file" \
      'BEGIN{tot=0} {if ($acc_col || $acc_col==0) tot+=1;} END{print tot;}' $data_file)
avg_acc=$(awk -v acc_col="$acc_col" -v data_file="$data_file" \
          'BEGIN{tot=0;}{tot+=$acc_col;}END{print tot / NR}' $data_file)
num_ones=$(awk -v acc_col="$acc_col" -v data_file="$data_file" \
          'BEGIN{tot=0;}{if ($acc_col == 1) tot+=1;}END{print tot}' $data_file)
num_over8=$(awk -v acc_col="$acc_col" -v data_file="$data_file" \
             'BEGIN{tot=0;}{if ($acc_col >= 0.8) tot+=1;}END{print tot}' $data_file)
num_over5under8=$(awk -v acc_col="$acc_col" -v data_file="$data_file" \
             'BEGIN{tot=0;}{if ($acc_col >= 0.5 && $acc_col < 0.8) tot+=1;}END{print tot}' $data_file)
num_over2under5=$(awk -v acc_col="$acc_col" -v data_file="$data_file" \
             'BEGIN{tot=0;}{if ($acc_col >= 0.2 && $acc_col < 0.5) tot+=1;}END{print tot}' $data_file)
num_zeroes=$(awk -v acc_col="$acc_col" -v data_file="$data_file" \
             'BEGIN{tot=0;}{if ($acc_col == 0) tot+=1;}END{print tot}' $data_file)
echo -e "Total number of accuracies:\t$tot"
echo -e "          Average accuracy:\t$avg_acc"
echo -e "             Number of 1's:\t$num_ones (ratio: $(bc <<< "scale=3; $num_ones / $tot;"))"
echo -e "           Number over 0.8:\t$num_over8 (ratio: $(bc <<< "scale=3; $num_over8 / $tot;"))"
echo -e "            0.5<= acc <0.8:\t$num_over5under8 (ratio: $(bc <<< "scale=3; $num_over5under8 / $tot;"))"
echo -e "            0.2<= acc <0.5:\t$num_over2under5 (ratio: $(bc <<< "scale=3; $num_over2under5 / $tot;"))"
echo -e "             Number of 0's:\t$num_zeroes (ratio: $(bc <<< "scale=3; $num_zeroes / $tot;"))"
