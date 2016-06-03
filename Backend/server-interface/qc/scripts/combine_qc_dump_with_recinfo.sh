#!/bin/bash 
# Copyright: 2016 Robert Kjaran <robert@kjaran.com>
help_message="Usage: $0  <parse-qc-dump-file>"
if [ $# -ne 1 -o "$1" = "--help" -o "$1" = "-h" ]; then
  echo "$help_message" >&2
  exit 1
fi
qc_dump=$1

query() {
   while read sessionId tokenId rest; do
     line=$(echo select recording.id, filename, inputToken, sessionId from recording, token where token.id=recording.tokenId and sessionId=$sessionId and tokenId=$tokenId ';' \
       | mysql -u root -D recordings_master --password="$pass" \
       | tail -n +2)
     # If "line" from sql db is not a single line, we just select the first one and
     # throw away the others, most of these should be garbage tests

     lno=$(echo "$line" | wc -l)
     if [ $lno -ne 1 ]; then
       echo "WARNING" >&2
       echo "line was: $line" >&2
     fi
     echo "$line" | head -n 1
   done
}

read -s -p "Mysql password:" pass

echo -e "# sessionId\ttokenId\taccuracy\tonlyInsOrSub\tcorrect\tsub\tins\tdel\tstartdel\tenddel\textraInsertions\tempty\tdistance\trecordingId\tfilename\ttoken\tsessionId"
paste <(tail -n +2 $qc_dump) \
      <(tail -n +2 $qc_dump | query)

#tail -n +2 $qc_dump | while read sessionId tokenId rest; do echo select recording.id, filename, inputToken, tokenId, sessionId from recording, token where sessionId=$sessionId and tokenId=$tokenId and tokenId=token.id ';'  | mysql -u root -D recordings_master --password="$pass" | wc -l
