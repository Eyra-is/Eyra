#!/bin/bash -eu

# Get the script directory
SDIR=$( dirname $( readlink -f $0 ) ) 

# load helper functions
. ${SDIR}/fn_report.sh

# Avoid problems when running as root
if [ "$(id -u)" == "0" ]; then
   report_err "This script should not be run as root." 1>&2
   exit 1
fi

available_opts=("ap"
                "apache"
                "mysqldb" 
                "backend-wsgi"
                "backend-db"
                "backend-204"
                "frontend-app"
                "ext-kaldi" )

declare -A AV_OPTS=(
['ap']='          WiFi Access Point'
['apache']='      Apache Web Server'
['mysqldb']='     MySQL Database'
['backend-wsgi']='WSGI for Apache'
['backend-db']='  Backend: Database Related'
['backend-204']=' Backend: Spoofing Android Online Check'
['frontend-app']='Frontend: Web App'
['ext-kaldi']='   External: Kaldi and dependencies'
)

usage () {
  echo "Usage:"
  echo "@0 [options] [config-file [...] ]"
  echo "config-file: Contain variable definitions. See /src/<xxx>/default.conf for defaults"
  echo "Options: (default: none)"
  echo "  --all           enable all options (excluding external)"
  echo "  --all-ext       enable all external options"
  echo "  --no-<xxx>      disable option <xxx>"
  echo "    ------------------------------"
  for i in ${!AV_OPTS[@]}; do
    echo "  --${i}  ${AV_OPTS[$i]}"
  done
  exit 0
}

declare -a CONF_FILES=
declare -A CONF_OPTS_TMP
while [ $# -gt 0 ]; do
  ARG=$1
  if [[ "${ARG:0:2}" == '--' ]]; then
    opt="${ARG:2}"
    CONF_OPTS_TMP+=([$opt]=true)
  else
    CONF_FILES+=( "$ARG" )
  fi
  shift
done

# check for contradicting options
for i in "${!CONF_OPTS_TMP[@]}"; do
  [[ "${i:0:3}" == "no-" ]] && [[ ${CONF_OPTS_TMP["${i:3}"]+isthere} ]] && {
    report_err "ERROR: You can not specify both --${i} and --${i:3}."
    exit 1
  }
done

declare -A CONF_OPTS
[[ ${CONF_OPTS_TMP["all"]+isthere} ]] && {
  # activating all options
  for opt in ${available_opts[@]}; do
    [[ ${CONF_OPTS_TMP["no-$opt"]+isthere} ]] || CONF_OPTS+=([$opt]=true)
  done
} || {
  for opt in ${!CONF_OPTS_TMP[@]}; do
     [[ "${opt:0:3}" == "no-" ]] || CONF_OPTS+=([$opt]=true)
  done
}

for opt in ${!CONF_OPTS[@]}; do
  [[ ${AV_OPTS["$opt"]+isthere} ]] || {
    report_err "ERROR: Unknown option '${opt}'."
    exit 1
  }
done

# Testing ${#CONF_OPTS[@]} gave an error for empty array...
# hence workaround
[[ -z "${CONF_OPTS[@]-}" ]] && {
  report "Nothing to do."
  echo
  usage
  exit 0
}

# source all default config files
for i in ${SDIR}/src/*/default.conf; do
  [[ -e ${i} ]] && . ${i}
done

# source user provided config files
for i in ${CONF_FILES[@]}; do
  report_nnl "Reading configuration in '${i}' ... "
  [[ -e ${i} ]] && . ${i} && suc || err  
done

# Get into a well defined directory
WDIR=$(readlink -f ${SDIR}/../Local )

report_nnl "Preparing working directory ${WDIR} ... "
mkdir -p ${WDIR} && cd ${WDIR} && suc || err
report_nnl "Preparing log directory ${WDIR}/Log for logging..." 
mkdir -p Log && suc || err

# get global dependencies
bash ${SDIR}/install_dependencies.sh ${SDIR}/src || err

GFILES=$(mktemp)
for opt in "${available_opts[@]}"; do
  [[ ${CONF_OPTS["$opt"]+isthere} ]] && {
    report "Setting up directory $(readlink -f ${SDIR}/src/${opt} )"
    . ${SDIR}/setup_component.sh ${SDIR}/src/$opt && suc || err
    [[ -f ${SDIR}/src/$opt/global.files ]] && \
      cat ${SDIR}/src/$opt/global.files >> $GFILES
  }
done

bash ${SDIR}/install_and_backup.sh $GFILES $WDIR/Root $WDIR/Bak

for opt in "${available_opts[@]}"; do
  [[ ${CONF_OPTS["$opt"]+isthere} ]] && {
    report "Activating $(readlink -f ${SDIR}/src/${opt} ) ..."
    [[ -f ${SDIR}/src/${opt}/post_install.sh ]] && \
      . ${SDIR}/src/${opt}/post_install.sh && suc || err
  }
done

exit 0
