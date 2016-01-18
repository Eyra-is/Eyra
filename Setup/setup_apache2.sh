#!/bin/bash -eu

# prepare the files needed to serve this stuff through Apache

[ $# -ge 1 ] && HOSTPORT="$1" || HOSTPORT='*:80'

HOSTPORT='*:80'
HOSTPORTSSL='_default_:443'

SDIR=$( dirname $( readlink -f $0 ) )
TDIR=$( dirname $SDIR )

SITEROOT=${TDIR}
LOGROOT=${TDIR}/log
PYNPROC=2
PYNTHREAD=5

mkdir -p $LOGROOT

cp ${SDIR}/tmpl/datatool_vhost.conf .
cp ${SDIR}/tmpl/datatool_ssl_vhost.conf .

sed -i \
    -e "s/XXXHOSTPORTXXX/$HOSTPORT/" \
    -e "s/XXXHOSTPORTSSLXXX/$HOSTPORTSSL/" \
    -e "s:XXXLOGROOTXXX:$LOGROOT:" \
    -e "s:XXXSITEROOTXXX:$SITEROOT:" \
    -e "s:XXXPYNPROCXXX:$PYNPROC:" \
    -e "s:XXXPYNTHREADXXX:$PYNTHREAD:" \
	datatool_vhost.conf \
    datatool_ssl_vhost.conf


