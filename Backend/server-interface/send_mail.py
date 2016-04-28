#!/usr/bin/python3
import os
import re
import datetime
import sys
import smtplib

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

import MySQLdb
from config import dbConst

import time
from socket import gethostname as hostname

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

SENDER = 'dataacquisitiontoolbox@gmail.com'
PASSWORD = 'CHANGE THIS THING'
EYRA_RECORDINGS_ROOT = '/data/eyra/recordings'


def dbConn():
    return MySQLdb.connect(**dbConst)

def countSessions(conn):
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM session')
    return cur.fetchone()[0]

def countRecordings(conn):
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM recording')
    return cur.fetchone()[0]

def recsByUser(conn):
    cur = conn.cursor()
    cur.execute('SELECT speaker.name, COUNT(*) '
                'FROM recording, speaker '
                'WHERE recording.speakerId = speaker.id '
                'GROUP BY recording.speakerId')
    return [(name, recCnt) for name, recCnt in cur.fetchall()]

def parseTimestampFromFilename(filename):
    timestamp = os.path.basename(filename).rsplit('.', maxsplit=1)[0]\
                                          .rsplit('_', maxsplit=1)[1]
    return datetime.datetime.strptime(
        re.sub(r'Z$', 'Z+0000', timestamp),
        '%Y-%m-%dT%H:%M:%S.%fZ%z')

def recsByDate(conn):
    cur = conn.cursor()
    # We get the filename, since that is currently the only available timestamp
    # the filename should be in format <username>_<ISO 8601>.wav
    cur.execute('SELECT filename FROM recording')
    timestamps = [parseTimestampFromFilename(row[0]) for row in cur.fetchall()]

    byDate = {}
    for ts in timestamps:
        byDate[ts.date()] = byDate.get(ts.date(), 0) + 1

    return sorted([(ts.strftime('%Y-%m-%d'), count) for ts, count in byDate.items()],
                  key=lambda x: x[0])

def recsByGender(conn):
    cur = conn.cursor()
    cur.execute('SELECT i.s_value, COUNT(*) FROM recording AS r, speaker_info AS i '
                'WHERE i.speakerId = r.speakerId AND (i.s_key = "sex" OR i.s_key = "gender") '
                'GROUP BY i.s_value')
    return [(gender, count) for gender, count in cur.fetchall()]

def recsByAge(conn):
    cur = conn.cursor()
    cur.execute('SELECT i.s_value, COUNT(*) FROM recording AS r, speaker_info AS i '
                'WHERE i.speakerId = r.speakerId AND i.s_key="dob" '
                'GROUP BY i.s_value')
    return [(year, count) for year, count in cur.fetchall()]

def recsByDevice(conn):
    cur = conn.cursor()
    cur.execute('SELECT deviceImei, COUNT(*) FROM recording, speaker '
                'WHERE recording.speakerId = speaker.id '
                'GROUP BY deviceImei')
    return [(deviceImei or 'No IMEI', count) for deviceImei, count in cur.fetchall()]

def recsByApkAndOs(conn):
    cur = conn.cursor()
    cur.execute('SELECT device.userAgent FROM recording, session, device '
                'WHERE recording.speakerId = session.speakerId AND session.deviceId = device.id '
                'GROUP BY recording.id ')
    def parseApkVersion(userAgent):
        m = re.search(r'App version: ([0-9\.]+) ', userAgent)
        if m:
            return m.group(0)
        else:
            return 'N/A'
    def parseOsVersion(userAgent):
        android = re.search(r'Android ([0-9\.]+)', userAgent)
        osx = re.search(r'Mac OS X ([0-9_\.]+)', userAgent)
        windows = re.search(r'Windows', userAgent)
        linux = re.search( r'X11;.*;? Linux', userAgent)

        if android:
            return 'Android {}'.format(android.group(1))
        elif osx:
            return 'Mac OSX {}'.format(osx.group(1))
        elif windows:
            return 'Windows (any version)'
        elif linux:
            return 'Linux (X11)'
        else:
            return 'Unkown OS'

    apkAndOsCounts = {}
    for userAgent in cur.fetchall():
        userAgent = userAgent[0]
        apkVer = parseApkVersion(userAgent)
        osGrp = parseOsVersion(userAgent)
        apkAndOsCounts['{} on {}'.format(apkVer, osGrp)] = apkAndOsCounts.get(
            '{} on {}'.format(apkVer, osGrp), 0) + 1

    return apkAndOsCounts.items()

def countTxt():
    "#: Deprecated"
    return len(glob('{}/session_*/*.txt'.format(EYRA_RECORDINGS_ROOT)))

def timestamp():
    return time.strftime('%Y-%m-%d %H:%M')

def main():
    recipients = sys.argv[1:]
    host = hostname()

    conn = dbConn()


    msg = MIMEMultipart()
    msg['Subject'] = 'Eyra at {} has recorded {} utterances'.format(host, countRecordings(conn))
    msg['To'] = ', '.join(recipients)
    msg['From'] = SENDER

    body = """
SUMMARY:
Recorded utterances: {recordings}
Distinct session count: {sessions}
""".format(recordings=countRecordings(conn), sessions=countSessions(conn))

    body += """
RECORDINGS BY USERNAME:
{lines}
""".format(lines='\n'.join(['{:<4} {}'.format(count, user)
                            for user, count in recsByUser(conn)]))

    # TODO: by date (we have to parse text...)
    #byDate

    body += """
RECORDINGS BY GENDER:
{lines}
""".format(lines='\n'.join('{:<6} {}'.format(count, gender)
                           for gender, count in recsByGender(conn)))

    body += """
RECORDINGS BY DAY:
{lines}
""".format(lines='\n'.join('{:<6} {}'.format(count, day)
                           for day, count in recsByDate(conn)))

    body += """
RECORDINGS BY AGE GROUP:
{lines}
""".format(lines='\n'.join('{:<6} {}'.format(count, year)
                           for year, count in recsByAge(conn)))

    body += """
RECORDINGS BY PHONE IMEI:
{lines}
""".format(lines='\n'.join('{:<4} {}'.format(count, imei)
                           for imei, count in recsByDevice(conn)))

    body += """
RECORDINGS BY APK AND OS:
{lines}
""".format(lines='\n'.join('{:<6} {}'.format(count, apkAndOs) for
                           apkAndOs, count in recsByApkAndOs(conn)))

    part = MIMEText('text', "plain")
    part.set_payload(body)
    msg.attach(part)

    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

    session.ehlo()
    session.starttls()
    session.ehlo

    session.login(SENDER, PASSWORD)
    session.sendmail(SENDER, recipients, msg.as_string())

    session.quit()

    sys.exit(0)

if __name__ == '__main__':
    main()
