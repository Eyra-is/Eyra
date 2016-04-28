#!/bin/bash
# Copyright:  2016  Robert Kjaran <robert@kjaran.com>
help_message="Usage: $0

Update schema, label current tokens and add labeled tokens.
"

DATABASE="recordings_master"
CURRENT_LABEL="jv"

if [ "$1" = "--help" -o "$1" = "-h" ]; then
  echo "$help_message"
  exit 0
fi

tmp=$(mktemp -d)
trap "rm -rf $tmp" EXIT

cat <<EOF > $tmp/alter_update.sql
SET collation_connection = 'utf8_general_ci';
ALTER TABLE token ADD COLUMN promptLabel VARCHAR(2) NOT NULL DEFAULT '';
UPDATE token SET promptLabel = '$CURRENT_LABEL';
EOF

python3 tokens_to_sql.py \
        --use-labels \
        ../db/src/jv/jv_extra_2016-04-28.txt \
        >> $tmp/alter_update.sql

mysql -u root -p $DATABASE < $tmp/alter_update.sql
