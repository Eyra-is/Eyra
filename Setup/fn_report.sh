# Copyright 2016 Simon Klüpfel 
# Apache 2.0

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

