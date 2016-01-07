from flask.ext.mysqldb import MySQL
from MySQLdb import Error as MySQLError
import json
import os # for mkdir
import random

from util import log

class DbHandler:
    def __init__(self, app):
        # MySQL configurations
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'default'
        app.config['MYSQL_DB']   = 'recordings_master'

        self.mysql = MySQL(app)

    # jsonData = look at format in the client-server API
    # recordings = an array of file objects representing the submitted recordings
    # returns a dict (msg=msg, statusCode=200,400,..)
    def processSessionData(self, jsonData, recordings):
        RECORDINGS_ROOT = 'recordings' # root path to recordings
        jsonDecoded = None
        sessionId = None
        output = ''

        # vars from jsonData
        speakerId, instructorId, deviceId, location, start, end, comments = \
            None, None, None, None, None, None, None

        if type(recordings)!=list or len(recordings)==0:
            msg = 'No recordings received, aborting.'
            log(msg)
            return dict(msg=msg, statusCode=400)

        # extract json data
        try:
            jsonDecoded = json.loads(jsonData)
            output += str(jsonDecoded)
     
            if jsonDecoded['type'] == 'session':
                jsonDecoded = jsonDecoded['data']
                speakerId = jsonDecoded['speakerId']
                instructorId = jsonDecoded['instructorId']
                deviceId = jsonDecoded['deviceId']
                location = jsonDecoded['location']
                start = jsonDecoded['start']
                end = jsonDecoded['end']
                comments = jsonDecoded['comments']
            else:
                msg = 'Wrong type of data.'
                log(msg)
                return dict(msg=msg, statusCode=400)

        except (KeyError, TypeError, ValueError) as e:
            msg = 'Session data not on correct format, aborting.'
            log(msg, e)
            return dict(msg=msg, statusCode=400)

        try: # one big try block simply for readability of code
            # insert into session
            cur = self.mysql.connection.cursor()

            # firstly, check if this session already exists, if so, update end time, otherwise add session
            cur.execute('SELECT id FROM session WHERE \
                         speakerId=%s AND instructorId=%s AND deviceId=%s AND location=%s AND start=%s',
                        (speakerId, instructorId, deviceId, location, start))
            sessionId = cur.fetchone()
            if (sessionId is None):
                # create new session entry in database
                cur.execute('INSERT INTO session (speakerId, instructorId, deviceId, location, start, end, comments) \
                             VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                            (speakerId, instructorId, deviceId, location, start, end, comments))
                # get the newly auto generated session.id 
                cur.execute('SELECT id FROM session WHERE \
                             speakerId=%s AND instructorId=%s AND deviceId=%s AND location=%s AND start=%s AND end=%s',
                            (speakerId, instructorId, deviceId, location, start, end))
                sessionId = cur.fetchone()[0] # fetchone returns a tuple
            else:
                # session already exists, simply update end-time
                sessionId = sessionId[0] # fetchone() returns tuple
                cur.execute('UPDATE session \
                             SET end=%s \
                             WHERE id=%s', 
                            (end, sessionId))
        
            # now populate recordings table

            # make sure path to recordings exists
            if not os.path.exists(RECORDINGS_ROOT):
                os.mkdir(RECORDINGS_ROOT)

            for rec in recordings:
                # save recordings to recordings/sessionId/filename
                sessionPath = os.path.join(RECORDINGS_ROOT, 'session_'+str(sessionId))
                if not os.path.exists(sessionPath):
                    os.mkdir(sessionPath)
                wavePath = os.path.join(sessionPath, rec.filename)
                rec.save(wavePath)

                # find duration
                duration = 0 # temp duration until we code it

                # insert into database
                cur.execute('INSERT INTO recording (tokenId, speakerId, sessionId, duration, rel_path) \
                             VALUES (%s, %s, %s, %s, %s)', 
                            (jsonDecoded['recordingsInfo'][rec.filename]['tokenId'], speakerId, 
                             sessionId, duration, wavePath))

            # only commit if we had no exceptions until this point
            self.mysql.connection.commit()

        except MySQLError as e:
            msg = 'Database error.'
            log(msg, e)
            return dict(msg=msg, statusCode=500)
        except os.error as e:
            msg = 'Error saving recordings to file.'
            log(msg, e)
            return dict(msg=msg, statusCode=500)
        except KeyError as e:
            msg = 'Missing recording info in session data.'
            log(msg, e)
            return dict(msg=msg, statusCode=400)

        return dict(msg='Successful process of session data.', statusCode=200)

    # gets numTokens tokens randomly selected from the database and returns them in a nice json format.
    # look at format in the client-server API
    # or it's: [{"id":id1, "token":token1}, {"id":id2, "token":token2}, ...]
    # returns [] on failure
    def getTokens(self, numTokens):
        tokens = []
        try:
            cur = self.mysql.connection.cursor()

            # select numTokens random rows from the database
            cur.execute('SELECT COUNT(*) FROM token');
            numRows = cur.fetchone()[0]
            # needs testing here to make sure 1 is lowest id, and numRows is highest id
            randIds = [random.randint(1,int(numRows)) for i in range(int(numTokens))]
            randIds = tuple(randIds) # change to tuple because SQL syntax is 'WHERE id IN (1,2,3,..)'
            cur.execute('SELECT id, inputToken FROM token WHERE id IN %s',
                        (randIds,)) # have to pass in a tuple, with only one parameter
            tokens = cur.fetchall()
        except MySQLError as e:
            msg = 'Error getting tokens from database.'
            log(msg, e)
            return dict(msg=msg, statusCode=500)

        jsonTokens = []
        # parse our tuple object from the cursor.execute into our desired json object
        for pair in tokens:
            jsonTokens.append({"id":pair[0], "token":pair[1]})

        return jsonTokens