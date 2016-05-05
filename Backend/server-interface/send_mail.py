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

class filterData():
    invalidIds = None # invalid rec ids, call filterOutUselessRecs if you use
    def setInvalidIds(self, i):
        self.invalidIds = i
    def getInvalidIds(self):
        return self.invalidIds
filterCommon = filterData()

invalidSpkrMatch = [
    'test'
]
invalidSpkrExact = [
    'Kevin', # sorry Kevin, I just don't buy that you speak Javanese
    'oddur',
    'rkr',
    'SveinnE',
    'Knot',
    'halli',
    'Demo',
    'jkjkjk',
    'Demo1',
    'Fghh',
    'Demo2',
    'Demo10',
    'Demo123',
    'Demo1234',
    'derp'
]
# exceptions
validSpkr = [
    'sonnysasaka'
]

def dbConn():
    return MySQLdb.connect(**dbConst)

def countSessions(conn):
    # do this instead, since session count really isn't robust, we really want this, how much we display per user after the filtering.
    return len(recsByUser(conn))
    # This code may not even work..
    # cur = conn.cursor()
    # cur.execute(listIntoMysqlQuery(
    #     'SELECT COUNT(*) FROM '
    #     '  (SELECT * FROM session, recording '
    #     '  WHERE recording.sessionId = session.id '
    #     '  AND recording.id NOT IN (%s) '
    #     '  GROUP BY session.id) AS ses', filterCommon.getInvalidIds()), tuple(filterCommon.getInvalidIds()))
    # return cur.fetchone()[0]

def countRecordings(conn):
    cur = conn.cursor()
    cur.execute(listIntoMysqlQuery(
        'SELECT COUNT(*) FROM '
        '  (SELECT * FROM recording '
        '   WHERE id NOT IN (%s)) AS recs', filterCommon.getInvalidIds()), tuple(filterCommon.getInvalidIds()))
    return cur.fetchone()[0]

def recsByUser(conn):
    cur = conn.cursor()
    cur.execute(listIntoMysqlQuery( 'SELECT speaker.name, COUNT(*) '
                                    'FROM recording, speaker '
                                    'WHERE recording.speakerId = speaker.id '
                                    '  AND recording.id NOT IN (%s) '
                                    'GROUP BY recording.speakerId', filterCommon.getInvalidIds()), tuple(filterCommon.getInvalidIds()))
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
    cur.execute(listIntoMysqlQuery(
        'SELECT filename FROM recording '
        'WHERE id NOT IN (%s)', filterCommon.getInvalidIds()), tuple(filterCommon.getInvalidIds()))
    timestamps = [parseTimestampFromFilename(row[0]) for row in cur.fetchall()]

    byDate = {}
    for ts in timestamps:
        byDate[ts.date()] = byDate.get(ts.date(), 0) + 1

    return sorted([(ts.strftime('%Y-%m-%d'), count) for ts, count in byDate.items()],
                  key=lambda x: x[0])

def recsByGender(conn):
    cur = conn.cursor()
    cur.execute(listIntoMysqlQuery(
        'SELECT i.s_value, COUNT(*) FROM recording AS r, speaker_info AS i '
        'WHERE i.speakerId = r.speakerId AND (i.s_key = "sex" OR i.s_key = "gender") '
        '  AND r.id NOT IN (%s) '
        'GROUP BY i.s_value', filterCommon.getInvalidIds()), tuple(filterCommon.getInvalidIds()))
    return [(gender, count) for gender, count in cur.fetchall()]

def recsByAge(conn):
    cur = conn.cursor()
    cur.execute(listIntoMysqlQuery(
        'SELECT i.s_value, COUNT(*) FROM recording AS r, speaker_info AS i '
        'WHERE i.speakerId = r.speakerId AND i.s_key="dob" '
        '  AND r.id NOT IN (%s) '
        'GROUP BY i.s_value', filterCommon.getInvalidIds()), tuple(filterCommon.getInvalidIds()))
    return [(year, count) for year, count in cur.fetchall()]

def recsByDevice(conn):
    cur = conn.cursor()
    cur.execute(listIntoMysqlQuery(
        'SELECT deviceImei, COUNT(*) FROM recording, speaker '
        'WHERE recording.speakerId = speaker.id '
        '  AND recording.id NOT IN (%s) '
        'GROUP BY deviceImei', filterCommon.getInvalidIds()), tuple(filterCommon.getInvalidIds()))
    return [(deviceImei or 'No IMEI', count) for deviceImei, count in cur.fetchall()]

def recsByApkAndOs(conn):
    cur = conn.cursor()
    cur.execute(listIntoMysqlQuery(
        'SELECT device.userAgent FROM recording, session, device '
        'WHERE recording.speakerId = session.speakerId AND session.deviceId = device.id '
        '  AND recording.id NOT IN (%s) '
        'GROUP BY recording.id ', filterCommon.getInvalidIds()), tuple(filterCommon.getInvalidIds()))
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

def filterOutUselessRecs(conn):
    """
    Very rough, returns ids of recordings we don't want.

    Filters out certain names, a low count of recordings and recordings before a certain date.

    Author: matthias
    """
    cur = conn.cursor()

    invalidIds = set()
    invalidRecCntThreshold = 10 # less than 10
    upperMatchThreshold = 200 # if invalidSpkrMatch is a match but recs over threshold, still display
    dateThreshold = datetime.date(2016, 5, 2) # exclude recordings from 1. may and prior

    # by name and recCnt < threshold
    cur.execute('SELECT speaker.name, speaker.id, COUNT(*) '
                'FROM recording, speaker '
                'WHERE recording.speakerId = speaker.id '
                'GROUP BY recording.speakerId')
    for name, speakerId, recCnt in cur.fetchall():
        for invalidMatch in invalidSpkrMatch:
            if name in invalidSpkrExact or (invalidMatch in name.lower() and recCnt < upperMatchThreshold) or recCnt < invalidRecCntThreshold:
                cur.execute('SELECT id '
                            'FROM recording '
                            'WHERE speakerId = %s' % speakerId)
                for recordingId in cur.fetchall():
                    invalidIds.add(recordingId[0])

    # by date

    # We get the filename, since that is currently the only available timestamp
    # the filename should be in format <username>_<ISO 8601>.wav
    cur.execute('SELECT filename, id FROM recording')
    timestamps = [(parseTimestampFromFilename(filename), recId) for filename, recId in cur.fetchall()]

    byDate = {}
    for ts, recId in timestamps:
        if ts.date() not in byDate:
            byDate[ts.date()] = []
        byDate[ts.date()].append(recId)

    for ts, recIds in byDate.items():
        yearDiff = dateThreshold.year - ts.year
        monthDiff = dateThreshold.month - ts.month
        if yearDiff < 0 or monthDiff < 0 or (dateThreshold - ts).days > 0:
            invalidIds.update(recIds)

    # remove ids belonging to the validSpkr
    query = 'SELECT recording.id '\
            'FROM recording, speaker '\
            'WHERE recording.speakerId = speaker.id '\
            '  AND speaker.name IN (%s)'
    query = listIntoMysqlQuery(query, validSpkr)
    cur.execute(query, tuple(validSpkr))
    for recId in cur.fetchall():
        try:
            invalidIds.remove(recId[0])
        except KeyError:
            pass

    invalidIds = tuple(invalidIds)
    filterCommon.setInvalidIds(invalidIds)

def listIntoMysqlQuery(query, data):
    return query % ','.join(['%s'] * len(data))

def main():
    recipients = sys.argv[1:]
    host = hostname()

    conn = dbConn()

    filterOutUselessRecs(conn)

    msg = MIMEMultipart()
    msg['Subject'] = 'Eyra at {} has recorded {} utterances'.format(host, countRecordings(conn))
    msg['To'] = ', '.join(recipients)
    msg['From'] = SENDER

    body = """
SUMMARY:
Recorded utterances: {recordings}
Distinct "session" count: {sessions}
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
