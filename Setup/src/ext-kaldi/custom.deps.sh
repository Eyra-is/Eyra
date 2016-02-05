#!/bin/bash -xeu

KALDI_COMMIT="88d78ad28d86dde470bdef0cb982a5ef32e9571f"

NPROC=$( nproc || grep -c "^processor" /proc/cpuinfo )

# install Kaldi into Local/opt/

# we assume this script is run from within Local/
mkdir -p opt && cd opt || exit 1

#get tested Kaldi revision
[[ ! -d kaldi-${KALDI_COMMIT} ]] && {
  wget -O ${KALDI_COMMIT}.zip https://github.com/kaldi-asr/kaldi/archive/${KALDI_COMMIT}.zip && \
  unzip ${KALDI_COMMIT}.zip && \
  ln -sf kaldi-${KALDI_COMMIT} kaldi-trunk || exit 1
}

cd kaldi-trunk && \
cd tools/ && \
sed -i -e "s:--enable-ngram-fsts CXX:--enable-ngram-fsts --enable-pdt CXX:" \
       -e "s:# OPENFST_VERSION = 1.4.1:OPENFST_VERSION = 1.4.1:" Makefile && \
make -j $NPROC all openblas

cd ../src/ && \
./configure --mathlib=OPENBLAS --openblas-root=../tools/OpenBLAS/install --use-cuda=no && \
make depend && \
make -j $NPROC && \
make ext && \
make test && \
make ext_test

exit $?
