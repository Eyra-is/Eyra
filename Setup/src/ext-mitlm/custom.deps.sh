#!/bin/bash -xeu

COMMIT="20cd196e10831269d459bbead70ff7acdda0c0a2"

SDIR=$( dirname $( readlink -f $0 ) )

NPROC=$( nproc || grep -c "^processor" /proc/cpuinfo )

# install into Local/opt/

# we assume this script is run from within Local/
mkdir -p opt && cd opt || exit 1

# get kenlam
tar -xzf ${SDIR}/src/${COMMIT}.zip && \
ln -sf mitlm-${COMMIT} mitlm && \
cd mitlm && \
make -j ${NPROC}

exit $?
