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
#
# Some possibly useful commands while parsing the QC dumps.

# get rid of duplicates in qc_dump_combined file by sorting on recording id
# removes header (you'll probably want to add that manually)
tail -n +2 qc_dump_combined.txt | sort -t $'\t' -u -k 15,15

# calculate average accuracy
awk 'BEGIN{tot=0;}{tot+=$3;}END{print tot / NR}' qc_dump_combined.txt

# remove all lines in qc_dump with tokens with specific promptlabels ('en')
mysql -u root -D "recordings_master" -e "select inputToken from token where promptLabel='en';"  | \
grep -v -f - qc_dump_combined.txt > qc_dump_combined_no_en.txt

# grab lowest scoring 300
tail -n +2 qc_dump_combined_no_en.txt | shuf | awk 'BEGIN{tot=0;} {if ($3 <= 0.3 && $12 != "true" && tot < 300) {print; tot+=1;}}' > worst300.txt

# grab highest scoring 300
tail -n +2 qc_dump_combined_no_en.txt | shuf | awk 'BEGIN{tot=0;} {if ($3 >= 0.9 && tot < 300) {print; tot+=1;}}' > best300.txt

# grab middle scoring 300
tail -n +2 qc_dump_combined_no_en.txt | shuf | awk 'BEGIN{tot=0;} {if ($3 > 0.3 && $3 < 0.9 && tot < 300) {print; tot+=1;}}' > mid300.txt

# grab and wrap the recordings mentioned in a file to a tarball
name=best300
mkdir "$name"
cut -f 15 "$name".txt | \
while read line; do 
    cp $(find -L /data/eyra/recordings -name "$line") "$name"/"$line" || echo "Failed to copy: $line"
    sleep 0.2
done
tar -czf "$name".tgz "$name" "$name".txt
rm -rf "$name"

# grab recordings and text files and compress (only recordings + prompts, not the qc analysis)
name=random1000
mkdir "$name"
cut -f 15 "$name".txt | \
while read line; do 
    # remove 4 letter extension
    wavname="${line%????}"
    file=$(find -L /data/eyra/recordings -name "$line")
    filename="${file%????}"
    cp "$filename".wav "$name"/"$wavname".wav || echo "Failed to copy: $line"
    cp "$filename".txt "$name"/"$wavname".txt || echo 'Failed to copy: "$wavname".txt'
    sleep 0.2
done
tar -czf "$name".tgz "$name"
rm -rf "$name"
