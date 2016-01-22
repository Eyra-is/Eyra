#!/bin/bash -eu

SDIR=$( dirname $( readlink -f $0 ) ) 
BDIR=$( dirname $SDIR )
ODIR=$( readlink -f ${BDIR}/Local )

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

mkdir -p $LOGROOT

# Get into the scripts directory
pushd $SDIR > /dev/null

# Install dependencies if needed
echo "Installing dependencies"

sudo aptitude update
sudo aptitude install $(cat deps_aptitude)
sudo pip3 install $(cat deps_pip3)

# 
mkdir -p ${ODIR}/bin/
cp ${SDIR}/bin/restart_network.sh ${ODIR}/bin


OFILE=${ODIR}/Root/etc/hostapd/hostapd.conf
mkdir -p $( dirname ${OFILE} )
sed -e "s/XXXWIFI_DEVXXX/${WIFI_DEV}/" \
    -e "s/XXXWIFI_DRIVERXXX/${WIFI_DRIVER}/" \
    -e "s/XXXWIFI_SSIDXXX/${WIFI_SSID}/" \
    -e "s/XXXWIFI_PASSXXX/${WIFI_PASS}/" \
    -e "s/XXXWIFI_CHANXXX/${WIFI_CHAN}/" \
    ${SDIR}/tmpl/etc_hostapd_hostapd.conf \
> ${OFILE}

OFILE=${ODIR}/Root/etc/network/interfaces
mkdir -p $( dirname ${OFILE} )
sed -e "s/XXXWIFI_DEVXXX/${WIFI_DEV}/" \
    -e "s/XXXWIFI_IPXXX/${WIFI_IP}/" \
    -e "s/XXXWIFI_NMASKXXX/${WIFI_NMASK}/" \
    -e "s/XXXWIFI_BCASTXXX/${WIFI_BCAST}/" \
    ${SDIR}/tmpl/etc_network_interfaces \
> ${OFILE}

OFILE=${ODIR}/Root/etc/default/hostapd
mkdir -p $( dirname ${OFILE} )
cp ${SDIR}/tmpl/etc_default_hostapd ${OFILE}

OFILE=${ODIR}/Root/etc/dnsmasq.conf
mkdir -p $( dirname ${OFILE} )
sed -e "s/XXXWIFI_DEVXXX/${WIFI_DEV}/" \
    -e "s/XXXWIFI_IPXXX/${WIFI_IP}/" \
    -e "s/XXXWIFI_DHCPSTAXXX/${WIFI_DHCPSTA}/" \
    -e "s/XXXWIFI_DHCPSTOXXX/${WIFI_DHCPSTO}/" \
    -e "s/XXXWIFI_DHCPLEAXXX/${WIFI_DHCPLEA}/" \
    ${SDIR}/tmpl/etc_dnsmasq.conf \
> ${OFILE}

OFILE=${ODIR}/Root/etc/apache2/sites-available/datatool.conf
mkdir -p $( dirname ${OFILE} )
sed -e "s/XXXHOST_NAMEXXX/$HOST_NAME/" \
    -e "s:XXXSITEROOTXXX:$SITEROOT:" \
    -e "s:XXXUSERXXX:$USER:" \
    -e "s:XXXGROUPXXX:$USER:" \
    -e "s:XXXWSGI_NPROCXXX:$WSGI_NPROC:" \
    -e "s:XXXWSGI_NTHREADXXX:$WSGI_NTHREAD:" \
    -e "s:XXXWSGIROOTXXX:$WSGIROOT:" \
    -e "s:XXXLOGROOTXXX:$LOGROOT:" \
    ${SDIR}/tmpl/etc_apache2_sites-available_datatool.conf \
> ${OFILE}


# install the files
sudo bash <<EOF
echo 'Checking for dnsmasq and hostapd...';
which dnsmasq > /dev/null && \
which hostapd > /dev/null || \
( aptitude -q  update && aptitude -q install hostapd dnsmasq );
echo "Backing up old configuration files...";
NBAK=\$( ls -1d ${ODIR}/Bak/*/ | wc -l )
mkdir -p ${ODIR}/Bak/\${NBAK};
(cd ${ODIR}/Root && find . -type f) | while read line; do
  mkdir -p ${ODIR}/Bak/\${NBAK}/\$( dirname \$line )
  cp /\$line ${ODIR}/Bak/\${NBAK}/\$line ;
  cp ${ODIR}/Root/\$line /\$line
done
if [ \$NBAK -ge 1 ]; then
  if diff -r ${ODIR}/Bak/\${NBAK} ${ODIR}/Bak/\$(( \${NBAK} - 1 )) > /dev/null ; then
    echo "Last Config unchanged. Not backing up."
    rm -r ${ODIR}/Bak/\${NBAK}
  fi  
fi
echo "Restarting Network..."
${ODIR}/bin/restart_network.sh
echo "WiFi Status:"
iw $WIFI_DEV info
EOF

echo
echo "Setting Up Apache"
for i in $(ls -1 /etc/apache2/sites-available/); do
  sudo a2dissite ${i}
done
sudo a2ensite datatool.conf
sudo a2enmod ssl wsgi
sudo service apache2 restart

echo
echo "All done"
echo "    SSID: $WIFI_SSID"
echo "    PASS: $WIFI_PASS"
echo "Have Fun!"


cd ${BDIR}/
