#!/bin/bash -xeu
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
#     Simon Klüpfel 

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
