from flask.ext.mysqldb import MySQL
import json
import os # for mkdir
import random

class DbHandler:
    def __init__(self, app):
        # MySQL configurations
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'default'
        app.config['MYSQL_DB']   = 'recordings_master'

        self.mysql = MySQL(app)        

    # jsonData = look at format in the client-server API
    # recordings = an array of file objects representing the submitted recordings
    def processSessionData(self, jsonData, recordings):
        RECORDINGS_ROOT = 'recordings' # root path to recordings
        jsonDecoded = None
        sessionId = None
        output = ''

        jsonDecoded = json.loads(jsonData)
        output += str(jsonDecoded)
        if jsonDecoded['type'] == 'session':
            jsonDecoded = jsonDecoded['data']
        else:
            return 'Wrong type of data.'

        cur = self.mysql.connection.cursor()

        # firstly, check if this session already exists, if so, update end time, otherwise add session
        cur.execute('SELECT id FROM session WHERE \
                     speakerId=%s AND instructorId=%s AND deviceId=%s AND location=%s AND start=%s',
                    (jsonDecoded['speakerId'], jsonDecoded['instructorId'], jsonDecoded['deviceId'],
                     jsonDecoded['location'], jsonDecoded['start']))
        sessionId = cur.fetchone()
        if (sessionId is None):
            # create new session entry in database
            cur.execute('INSERT INTO session (speakerId, instructorId, deviceId, location, start, end, comments) \
                         VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                        (jsonDecoded['speakerId'], jsonDecoded['instructorId'], jsonDecoded['deviceId'],
                         jsonDecoded['location'], jsonDecoded['start'], jsonDecoded['end'], jsonDecoded['comments']))
            # get the newly auto generated session.id 
            cur.execute('SELECT id FROM session WHERE \
                         speakerId=%s AND instructorId=%s AND deviceId=%s AND location=%s AND start=%s AND end=%s',
                        (jsonDecoded['speakerId'], jsonDecoded['instructorId'], jsonDecoded['deviceId'],
                         jsonDecoded['location'], jsonDecoded['start'], jsonDecoded['end']))
            sessionId = cur.fetchone()[0] # fetchone returns a tuple
        else:
            # session already exists, simply update end-time
            sessionId = sessionId[0] # fetchone() returns tuple
            cur.execute('UPDATE session \
                         SET end=%s \
                         WHERE id=%s', 
                        (jsonDecoded['end'], sessionId))

        # now populate recordings table
        #
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
                        (jsonDecoded['recordingsInfo'][rec.filename]['tokenId'], jsonDecoded['speakerId'], 
                         sessionId, duration, wavePath))

        # only commit if we had no exceptions until this point
        self.mysql.connection.commit()

        return 'Successful process of session data.\n'

    # gets numTokens tokens randomly selected from the database and returns them in a nice json format.
    # look at format in the client-server API
    # or it's: [{"id":id1, "token":token1}, {"id":id2, "token":token2}, ...]
    def getTokens(self, numTokens):
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

        jsonTokens = []
        # parse our tuple object from the cursor.execute into our desired json object
        for pair in tokens:
            jsonTokens.append({"id":pair[0], "token":pair[1]})

        return json.dumps(jsonTokens)