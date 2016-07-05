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
#     Simon Klüpfel <simon.kluepfel@gmail.com> 

KALDI_COMMIT="ce708ea1679467b915d50c5439eeb41a249e2d32"

NPROC=$( nproc || grep -c "^processor" /proc/cpuinfo )

# install Kaldi into Local/opt/

# we assume this script is run from within Local/
mkdir -p opt && cd opt || exit 1

CHECKFILE=$(realpath -s -m ext-kaldi.done)

[[ -f $CHECKFILE ]] && {
  echo "Kaldi seems to be set up already."
  echo "For a reinstall, first delete $CHECKFILE"
  exit 0
}

#get tested Kaldi revision
[[ ! -d kaldi-${KALDI_COMMIT} ]] && {
  wget -O ${KALDI_COMMIT}.zip https://github.com/kaldi-asr/kaldi/archive/${KALDI_COMMIT}.zip && \
  unzip ${KALDI_COMMIT}.zip && \
  ln -sf kaldi-${KALDI_COMMIT} kaldi-trunk || exit 1
}

cd kaldi-trunk && \
cd tools/ && \
sed -i -e "s:--enable-ngram-fsts CXX:--enable-ngram-fsts --enable-pdt --enable-lookahead-fsts --enable-const-fsts --enable-linear-fsts CXX:" \
       -e "s:# OPENFST_VERSION = 1.4.1:OPENFST_VERSION = 1.4.1:" Makefile && \
make -j $NPROC all

cd ../src/ && \
./configure --mathlib=OPENBLAS --openblas-root=/usr --use-cuda=no && \
make depend && \
make -j $NPROC && \
touch $CHECKFILE

exit $?
