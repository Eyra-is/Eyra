#!/bin/bash -eu

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

[[ "$#" == "1" ]] || {
  echo "$0: This script needs exactly one argument!"
  exit 1
}

SRCDIR=$( realpath -s $1 )
TNAME=$( basename ${SRCDIR} )

BDIR=$( dirname $( realpath -s ${BASH_SOURCE[0]} ) )

# get dependencies
bash ${BDIR}/install_dependencies.sh ${SRCDIR} || err

SEDF=${TNAME}.sed

# preparing the sed script
[[ -f ${SRCDIR}/default.conf ]] && {
cut -d "=" -f 1 ${SRCDIR}/default.conf | \
  grep -v -e "^#" | grep -v -e "^ *$" | \
  while read var; do
    if [[ "${var:0:4}" == "YYY_" ]]; then
      echo "s|XXX${var:4}XXX|$(realpath -s ${BDIR}/../${!var})|"
    else
      echo "s|XXX${var}XXX|${!var}|"
    fi
  done > ${SEDF}
} || {
  : > ${SEDF}
}

echo "s|XXXUSERXXX|$USER|" >> ${SEDF}
echo "s|XXXGROUPXXX|$USER|" >> ${SEDF}

# Files to be installed globally
[[ -e ${SRCDIR}/global.files ]] && \
for f in $( cat ${SRCDIR}/global.files ); do 
  OUTF=Root${f}
  RSTR=${f//\//_}
  INF=${SRCDIR}/tmpl/${RSTR:1}
  parse_file $INF $OUTF $SEDF
echo $INF $OUTF $SEDF
done

# Globally installed files to be modified
[[ -e ${SRCDIR}/global.mod.files ]] && \
cat ${SRCDIR}/global.mod.files | while read line; do 
  F=( $line )
  FILE="${F[0]}"
  COMS="${F[@]:1}"
  if [[ ! -z "$COMS" ]]; then
    eval $COMS > Root${FILE}
  fi
done

[[ -e ${SRCDIR}/local.files ]] && \
for f in $( cat ${SRCDIR}/local.files ); do 
  OUTF=${f:1}
  RSTR=${f//\//_}
  INF=${SRCDIR}/tmpl/${RSTR:1}
  parse_file $INF $OUTF $SEDF
done

return 0
