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
