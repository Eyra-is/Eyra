#!/bin/bash -xeu
# Copyright 2016 Simon Klüpfel 
# Apache 2.0

COMMIT="dbd09a0db94d29099bb81c958c63bce74a976fc2"

NPROC=$( nproc || grep -c "^processor" /proc/cpuinfo )

# install Phonetisaurus into Local/opt/

# we assume this script is run from within Local/
mkdir -p opt && cd opt || exit 1

CHECKFILE=$( realpath -s -m ext-phoneti.done )

[[ -f $CHECKFILE ]] && {
  echo "Phonetisaurus seems to be set up already."
  echo "For a reinstall, first delete $CHECKFILE"
  exit 0
}

# get tested revision
[[ ! -d Phonetisaurus-${COMMIT} ]] && {
  wget -O ${COMMIT}.zip https://github.com/AdolfVonKleist/Phonetisaurus/archive/${COMMIT}.zip && \
  unzip -o ${COMMIT}.zip && \
  ln -sf Phonetisaurus-${COMMIT} Phonetisaurus || exit 1
}

cd Phonetisaurus && \
mkdir -p bin && \
mkdir -p lib && \
cd src && \
./configure --with-install-bin=$( realpath -s -m ../bin) \
            --with-install-lib=$( realpath -s -m ../lib) \
            --with-openfst-libs=../../kaldi-trunk/tools/openfst/lib \
            --with-openfst-includes=../../kaldi-trunk/tools/openfst/include && \
make -j $NPROC && \
make install && \
touch $CHECKFILE

exit $?
