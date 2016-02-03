#!/bin/bash -eu

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

[[ "$#" == "1" ]] || {
  echo "$0: This script needs exactly one argument!"
  exit 1
}

SRCDIR=$( realpath -s $1 )
TNAME=$( basename ${SRCDIR} )

BDIR=$( dirname $( realpath -s ${BASH_SOURCE[0]} ) )

# get dependencies
bash ${BDIR}/install_dependencies.sh ${SRCDIR} || err

SEDF=${TNAME}.sed

# preparing the sed script
[[ -f ${SRCDIR}/default.conf ]] && {
cut -d "=" -f 1 ${SRCDIR}/default.conf | \
  grep -v -e "^#" | grep -v -e "^ *$" | \
  while read var; do
    if [[ "${var:0:4}" == "YYY_" ]]; then
      echo "s|XXX${var:4}XXX|$(realpath -m -s ${BDIR}/../${!var})|"
    else
      echo "s|XXX${var}XXX|${!var}|"
    fi
  done > ${SEDF}
} || {
  : > ${SEDF}
}

echo "s|XXXUSERXXX|$USER|" >> ${SEDF}
echo "s|XXXGROUPXXX|$USER|" >> ${SEDF}

[[ -e ${SRCDIR}/global.files ]] && \
for f in $( cat ${SRCDIR}/global.files ); do 
  OUTF=Root${f}
  RSTR=${f//\//_}
  INF=${SRCDIR}/tmpl/${RSTR:1}
  parse_file $INF $OUTF $SEDF
done

[[ -e ${SRCDIR}/local.files ]] && \
for f in $( cat ${SRCDIR}/local.files ); do 
  OUTF=${f:1}
  RSTR=${f//\//_}
  INF=${SRCDIR}/tmpl/${RSTR:1}
  parse_file $INF $OUTF $SEDF
done

return 0





# Placing scripts
report "Placing control scripts in ${ODIR}/bin/ ..."
mkdir -p ${ODIR}/bin/ && \
cp ${SDIR}/bin/*.sh ${ODIR}/bin/ && suc || err

# Preparing config files
report "Setting up config files..."

mkdir -p ${ODIR}/Root/
rm -rf ${ODIR}/Root/*

# install the files

report 'Checking for dnsmasq and hostapd...'
sudo which dnsmasq hostapd > /dev/null || \
( sudo aptitude -q2 update && sudo aptitude -y install hostapd dnsmasq ) && suc || err

report "Backing up old configuration files...";
mkdir -p ${ODIR}/Bak/
NBAK=$( ls -1d ${ODIR}/Bak/*/ | wc -l )
report "Found $NBAK backup(s)."
mkdir -p ${ODIR}/Bak/${NBAK} && cd ${ODIR}/Root && find . -type f | while read line; do
  if [[ -e $line ]] ; then
    mkdir -p ${ODIR}/Bak/${NBAK}/$( dirname $line )
    cp /$line ${ODIR}/Bak/${NBAK}/$line ;
    sudo cp ${ODIR}/Root/$line /$line
  fi
done && suc || err

if [ $NBAK -ge 1 ]; then
  if diff -r ${ODIR}/Bak/${NBAK} ${ODIR}/Bak/$(( ${NBAK} - 1 )) > /dev/null ; then
    report "Last Config unchanged. Reverting backup..."
    rm -r ${ODIR}/Bak/${NBAK} && suc || err
  fi
fi

report  "Restarting Network..."
sudo ${ODIR}/bin/restart_wifi_ap.sh && suc || err

report "WiFi Status:"
sudo iw $WIFI_DEV info

# Setting up the frontend
report "Setting up Frontend ..."
${BDIR}/Frontend/da-webapp/set_me_up.sh && suc || err


report "Setting Up Apache ..."
for i in $(ls -1 /etc/apache2/sites-available/); do
  sudo a2dissite ${i} 
done && \
sudo a2ensite datatool.conf && \
sudo a2enmod ssl wsgi && \
sudo service apache2 restart && suc || err

report "All done"
report "    SSID: $WIFI_SSID"
report "    PASS: $WIFI_PASS"
report "Have Fun!"
echo

# Setting up the backend
report "Did not touch any MySQL stuff."
report "Run: ${BDIR}/Backend/db/erase_and_rewind.sh to setup MySQL database"
report_err "WARNING: All Databases will be dropped then..."




