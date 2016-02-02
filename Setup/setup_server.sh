#!/bin/bash -eu

color() {
      printf '\033[%sm%s\033[m\n' "$@"
      # usage color "31;5" "string"
      # 0 default
      # 5 blink, 1 strong, 4 underlined
      # fg: 31 red,  32 green, 33 yellow, 34 blue, 35 purple, 36 cyan, 37 white
      # bg: 40 black, 41 red, 44 blue, 45 purple
      }

report () {
  color "32;1" "$@"
}

report_err () {
  color "31;1" "$@"
}

# Avoid problems when running as root
if [ "$(id -u)" == "0" ]; then
   report_err "This script should not be run as root." 1>&2
   exit 1
fi

# file including the '. /etc/default/locale' line to be uncommented for utf8 support
ENVVARS='/etc/apache2/envvars'

SDIR=$( dirname $( readlink -f $0 ) ) 
BDIR=$( dirname $SDIR )
ODIR=$( readlink -f ${BDIR}/Local )

# These should probably be read from a config file
# for now keep it here...
WIFI_DEV=wlan0
WIFI_DRIVER=nl80211
WIFI_SSID=FeedMeData
WIFI_PASS=ThisIsSparta
WIFI_CHAN=8
WIFI_IP=192.168.8.1
WIFI_NMASK=255.255.255.0
WIFI_BCAST=192.168.8.255
WIFI_DHCPSTA=192.168.8.20
WIFI_DHCPSTO=192.168.8.220
WIFI_DHCPLEA=12h

HOST_PORT='*:80'
HOST_PORTSSL='_default_:443'
HOST_NAME='www.dasistder.net'

SITEROOT=${BDIR}/Frontend/da-webapp/app
WSGIROOT=${BDIR}/WSGI
LOGROOT=${ODIR}/Log

WSGI_NPROC=2
WSGI_NTHREAD=5

# end of configuration section

suc () {
  report "success!"
  echo
  return 0
}

err () {
  report_err "failure!"
  echo 
  return 1
}

report "Creating Directory $LOGROOT for logging..." 
mkdir -p $LOGROOT && suc || err

# Get into the scripts directory
pushd $SDIR > /dev/null

# Install dependencies if needed
report "Installing dependencies..."
sudo aptitude -q2 update && \
sudo aptitude -y install $(cat deps_aptitude) && \
sudo pip3 install $(cat deps_pip3) && suc || err

# Placing scripts
report "Placing control scripts in ${ODIR}/bin/ ..."
mkdir -p ${ODIR}/bin/ && \
cp ${SDIR}/bin/*.sh ${ODIR}/bin/ && suc || err

# Preparing config files
report "Setting up config files..."

mkdir -p ${ODIR}/Root/
rm -rf ${ODIR}/Root/*

cat > ${ODIR}/rep.sed <<EOF
s:XXXGROUPXXX:$USER:
s/XXXHOST_NAMEXXX/$HOST_NAME/
s:XXXLOGROOTXXX:$LOGROOT:
s:XXXSITEROOTXXX:$SITEROOT:
s:XXXUSERXXX:$USER:
s/XXXWIFI_BCASTXXX/${WIFI_BCAST}/
s/XXXWIFI_CHANXXX/${WIFI_CHAN}/
s/XXXWIFI_DEVXXX/${WIFI_DEV}/
s/XXXWIFI_DHCPLEAXXX/${WIFI_DHCPLEA}/
s/XXXWIFI_DHCPSTAXXX/${WIFI_DHCPSTA}/
s/XXXWIFI_DHCPSTOXXX/${WIFI_DHCPSTO}/
s/XXXWIFI_DRIVERXXX/${WIFI_DRIVER}/
s/XXXWIFI_IPXXX/${WIFI_IP}/
s/XXXWIFI_NMASKXXX/${WIFI_NMASK}/
s/XXXWIFI_PASSXXX/${WIFI_PASS}/
s/XXXWIFI_SSIDXXX/${WIFI_SSID}/
s:XXXWSGI_NPROCXXX:$WSGI_NPROC:
s:XXXWSGI_NTHREADXXX:$WSGI_NTHREAD:
s:XXXWSGIROOTXXX:$WSGIROOT:
EOF

parse_file () {
TMPLF=$1
OUTF=$2
[[ $# -gt 2 ]] && SUBF=$3 || SUBF=""
report "Processing template $TMPLF ..."
mkdir -p $( dirname ${OUTF} ) && \
if [[ -z $SUBF ]]; then
  cp $TMPLF $OUTF
else
  sed -f "$SUBF" $TMPLF > $OUTF
fi && suc || err
}

parse_file \
  ${SDIR}/tmpl/etc_hostapd_hostapd.conf \
  ${ODIR}/Root/etc/hostapd/hostapd.conf \
  ${ODIR}/rep.sed  

parse_file \
  ${SDIR}/tmpl/etc_network_interfaces.d_wlan0.conf \
  ${ODIR}/Root/etc/network/interfaces.d/wlan0.conf \
  ${ODIR}/rep.sed

parse_file \
  ${SDIR}/tmpl/etc_network_interfaces \
  ${ODIR}/Root/etc/network/interfaces

parse_file \
  ${SDIR}/tmpl/etc_default_hostapd \
  ${ODIR}/Root/etc/default/hostapd

parse_file \
  ${SDIR}/tmpl/etc_dnsmasq.conf \
  ${ODIR}/Root/etc/dnsmasq.conf \
  ${ODIR}/rep.sed

parse_file \
  ${SDIR}/tmpl/etc_apache2_sites-available_datatool.conf \
  ${ODIR}/Root/etc/apache2/sites-available/datatool.conf \
  ${ODIR}/rep.sed

# uncomment '. /etc/default/locale' line to use default locale (handle utf8)
report "Uncommenting default locale line in ${ENVVARS}..."
sudo sed -i 's/#\. \/etc\/default\/locale/\. \/etc\/default\/locale/' ${ENVVARS} && suc || err


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




