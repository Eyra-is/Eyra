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

color() {
      printf '\033[%sm%s\033[m' "$@"
      # usage color "31;5" "string"
      # 0 default
      # 5 blink, 1 strong, 4 underlined
      # fg: 31 red,  32 green, 33 yellow, 34 blue, 35 purple, 36 cyan, 37 white
      # bg: 40 black, 41 red, 44 blue, 45 purple
      }

report_nnl () {
  color "32;1" "$@"
}

report () {
    report_nnl "$@"
    echo
}

report_err_nnl () {
  color "31;1" "$@"
}

report_err () {
    report_err_nnl "$@"
    echo
}

suc () {
  report "success!"
  echo
  return 0
}

err () {
  report_err "failure!" >&2
  echo >&2
  return 1
}

parse_file () {
  TMPLF=$1
  OUTF=$2
  [[ $# -gt 2 ]] && SUBF=$3 || SUBF=""
  report_nnl "Processing template $TMPLF ... "
  mkdir -p $( dirname ${OUTF} ) && \
  if [[ -z $SUBF ]]; then
    cp $TMPLF $OUTF
  else
    sed -f "$SUBF" $TMPLF > $OUTF
  fi && suc || err
}

