from flask.ext.mysqldb import MySQL
from MySQLdb import Error as MySQLError
import json
import os # for mkdir
import random

from util import log, filename

class DbHandler:
    def __init__(self, app):
        # MySQL configurations
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'default'
        app.config['MYSQL_DB']   = 'recordings_master'
        app.config['MYSQL_USE_UNICODE'] = True
        app.config['MYSQL_CHARSET'] = 'utf8'

        self.mysql = MySQL(app)

        # needed to sanitize the dynamic sql creation in insertGeneralData
        # keep a list of allowed column names for insertions etc. depending on the table (device, isntructor, etc)
        self.allowedColumnNames = {
            'device': [
                'userAgent',
                'imei'
            ],
            'instructor': [
                'name',
                'email',
                'phone',
                'address'
            ],
            'speaker': [
                'name',
                'gender',
                'height',
                'dob',
                'deviceImei'
            ]
        }

    # inserts data into appropriate table
    #
    # name is i.e. 'instructor' and is a representation of the data, for errors and general identification
    # data is a json object whose keys will be used as table column names and those values
    #   will be inserted into table
    # returns the id of the newly inserted row or errors in the format
    #   dict(msg=id or msg, statusCode=htmlStatusCode)
    #
    # Example:
    #    name='device'
    #    data = {'imei':245, 'userAgent':'Mozilla'}
    #    table = 'device'
    #
    #    In which case, this function will 
    #    insert into device (imei, userAgent) 
    #                values ('245','Mozilla')
    #    and return said rows newly generated id.
    #
    # WARNING: appends the keys of data straight into a python string using %
    #          so at least this should be sanitized. Sanitized by a whitelist of
    #          allowed keys in self.allowedColumnNames
    def insertGeneralData(self, name, data, table):
        keys = []
        vals = []
        dataId = None
        try:
            if isinstance(data, str):
                data = json.loads(data)

            for key, val in data.items(): # use data.iteritems() for python 2.7
                # allow only keys from the appropriate list in self.allowedColumnNames
                if key not in self.allowedColumnNames[name]:
                    raise KeyError('Unallowed column name used! Did someone hack the frontend? name: %s' % key)
                keys.append(key)
                vals.append(val)

            data = None # data is untrusted, should not be used unless it's filtered
        except (KeyError, TypeError, ValueError) as e:
            msg = '%s data not on correct format, aborting.' % name
            log(msg, e)
            return dict(msg=msg, statusCode=400)

        try: 
            # insert into table
            cur = self.mysql.connection.cursor()

            # make our query something like (with 4 key/value pairs)
            # 'INSERT INTO %s (%s, %s, %s, %s) \
            #              VALUES (%s, %s, %s, %s)',
            # depending on number of data keys/values 
            queryStr = 'INSERT INTO %s ('

            queryStrMid = '' # since we can reuse the (%s,%s,...)
            for i in range(len(keys)):
                queryStrMid += '%s'
                if (i != len(keys) - 1):
                    queryStrMid += ', '

            queryStr += queryStrMid
            queryStr += ') '

            # input the keys first, because we don't want the '' quotes that cur.execute
            #   automatically puts there
            queryStr = queryStr % tuple([table] + keys)

            queryStr += 'VALUES ('
            queryStr += queryStrMid
            queryStr += ')'

            # make the replacement tuple which is set in place of the %s's in the query
            queryTuple = tuple(vals)

            cur.execute(queryStr, queryTuple)

            # get the newly auto generated id

            # create our query something like
            # 'SELECT id FROM %s WHERE \
            #              %s=%s AND %s=%s AND %s=%s AND %s=%s'
            # but now the order is WHERE key=val AND key1=val1 and so
            # we have to interleave our lists instead of appending them 
            # to get the correct order 
            interleavedList = []
            for i in range(len(keys)):
                interleavedList.append(keys[i])
                # just a hack, because of the quote thing mentioned above
                #   will be replaces with vals in query
                interleavedList.append('%s') 
            
            queryStr = 'SELECT id FROM %s WHERE '
            for i in range(len(keys)):
                queryStr += '%s=%s'
                if (i != len(keys) - 1):
                    queryStr += ' AND '

            queryStr = queryStr % tuple([table] + interleavedList)

            cur.execute(queryStr, queryTuple)
            dataId = cur.fetchone()[0] # fetchone returns a tuple

            # only commit if we had no exceptions until this point
            self.mysql.connection.commit()

        except MySQLError as e:
            msg = 'Database error.'
            log(msg, e)
            return dict(msg=msg, statusCode=500)

        if dataId is None:
            msg = 'Couldn\'t get %s id.' % name
            log(msg)
            return dict(msg=msg, statusCode=500)
        else:
            return dict(msg='{"%sId":' % name + str(dataId) + '}', statusCode=200)

    # instructorData = look at format in the client-server API
    def processInstructorData(self, instructorData):
        try:
            if isinstance(instructorData, str):
                instructorData = json.loads(instructorData)
        except (ValueError) as e:
            msg = '%s data not on correct format, aborting.' % name
            log(msg, e)
            return dict(msg=msg, statusCode=400)

        if 'id' in instructorData:
            # instructor was submitted as an id, see if he exists in database
            try: 
                cur = self.mysql.connection.cursor()

                cur.execute('SELECT id FROM instructor WHERE id=%s', (instructorData['id'],)) # have to pass in a tuple, with only one parameter
                instructorId = cur.fetchone()
                if (instructorId is None):
                    # no instructor
                    msg = 'No instructor with that id.'
                    log(msg)
                    return dict(msg=msg, statusCode=400)
                else:
                    # instructor already exists, return it
                    instructorId = instructorId[0] # fetchone returns tuple on success
                    return dict(msg='{"instructorId":' + str(instructorId) + '}', statusCode=200)
            except MySQLError as e:
                msg = 'Database error.'
                log(msg, e)
                return dict(msg=msg, statusCode=500)
            return 'Unexpected error.', 500

        return self.insertGeneralData('instructor', instructorData, 'instructor')

    def processDeviceData(self, deviceData):
        # we have to make sure not to insert device with same IMEI
        #   as is already in the database if so. Otherwise, we create new device
        deviceImei = None
        try:
            if isinstance(deviceData, str):
                deviceData = json.loads(deviceData)
            deviceImei = deviceData['imei']
        except (TypeError, ValueError) as e:
            msg = 'Device data not on correct format, aborting.'
            log(msg, e)
            return dict(msg=msg, statusCode=400)
        except (KeyError) as e:
            # we don't care if device has no ['imei']
            pass

        if deviceImei is not None and deviceImei != '':
            try: 
                cur = self.mysql.connection.cursor()

                # firstly, check if this device already exists, if so, update end time, otherwise add device
                cur.execute('SELECT id FROM device WHERE imei=%s', (deviceImei,)) # have to pass in a tuple, with only one parameter
                deviceId = cur.fetchone()
                if (deviceId is None):
                    # no device with this imei in database, insert it
                    return self.insertGeneralData('device', deviceData, 'device')
                else:
                    # device already exists, return it
                    deviceId = deviceId[0] # fetchone returns tuple on success
                    return dict(msg='{"deviceId":' + str(deviceId) + '}', statusCode=200)
            except MySQLError as e:
                msg = 'Database error.'
                log(msg, e)
                return dict(msg=msg, statusCode=500)

        # no imei present, wouldn't be able to recognize the device
        return self.insertGeneralData('device', deviceData, 'device')

    def processSpeakerData(self, speakerData):
        # we have to make sure not to insert device with same IMEI
        #   as is already in the database if so. Otherwise, we create new device
        name, gender, height, dob, deviceImei = None, None, None, None, None
        try:
            if isinstance(speakerData, str):
                speakerData = json.loads(speakerData)
            name = speakerData['name']
            gender = speakerData['gender']
            height = speakerData['height']
            dob = speakerData['dob']
        except (KeyError, TypeError, ValueError) as e:
            msg = 'Speaker data not on correct format, aborting.'
            log(msg, e)
            return dict(msg=msg, statusCode=400)

        try:
            deviceImei = speakerData['deviceImei']
        except (KeyError) as e:
            # we don't care if speaker has no ['imei']
            pass

        if deviceImei is not None and deviceImei != '':
            try: 
                cur = self.mysql.connection.cursor()

                # firstly, check if this speaker already exists, if so, update end time, otherwise add speaker
                cur.execute('SELECT id FROM speaker WHERE \
                         name=%s AND gender=%s AND height=%s AND dob=%s AND deviceImei=%s',
                        (name, gender, height, dob, deviceImei))
                speakerId = cur.fetchone()   # it's possible there are more than 1 speaker, in which case just fetch anyone, 
                                                # it's the statistical data that matters anyway
                if (speakerId is None):
                    # no speaker with this info in database, insert it
                    return self.insertGeneralData('speaker', speakerData, 'speaker')
                else:
                    # speaker already exists, return it
                    speakerId = speakerId[0] # fetchone returns tuple on success
                    return dict(msg='{"speakerId":' + str(speakerId) + '}', statusCode=200)
            except MySQLError as e:
                msg = 'Database error.'
                log(msg, e)
                return dict(msg=msg, statusCode=500)

        # no imei present, wouldn't be able to recognize the speaker
        return self.insertGeneralData('speaker', speakerData, 'speaker')

    # jsonData = look at format in the client-server API
    # recordings = an array of file objects representing the submitted recordings
    # returns a dict (msg=msg, statusCode=200,400,..)
    def processSessionData(self, jsonData, recordings):
        RECORDINGS_ROOT = 'recordings' # root path to recordings
        jsonDecoded = None
        sessionId = None

        # vars from jsonData
        speakerId, instructorId, deviceId, location, start, end, comments = \
            None, None, None, None, None, None, None
        speakerName = None

        if type(recordings)!=list or len(recordings)==0:
            msg = 'No recordings received, aborting.'
            log(msg)
            return dict(msg=msg, statusCode=400)

        # extract json data
        try:
            jsonDecoded = json.loads(jsonData)
            log(jsonDecoded)
     
            if jsonDecoded['type'] == 'session':
                jsonDecoded = jsonDecoded['data']
                # this inserts speaker into database
                speakerId = json.loads(
                                self.processSpeakerData(
                                    jsonDecoded['speakerInfo']
                                )['msg']
                            )['speakerId']
                instructorId = jsonDecoded['instructorId']
                # this inserts device into database
                deviceId =  json.loads(
                                self.processDeviceData(
                                    jsonDecoded['deviceInfo']
                                )['msg']
                            )['deviceId']
                location = jsonDecoded['location']
                start = jsonDecoded['start']
                end = jsonDecoded['end']
                comments = jsonDecoded['comments']
                speakerName = jsonDecoded['speakerInfo']['name']
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
        
            # now populate recordings table and save recordings+extra data to file/s

            # make sure path to recordings exists
            if not os.path.exists(RECORDINGS_ROOT):
                os.mkdir(RECORDINGS_ROOT)

            for rec in recordings:
                # grab token to save as extra metadata later
                tokenId = jsonDecoded['recordingsInfo'][rec.filename]['tokenId']
                cur.execute('SELECT inputToken FROM token WHERE id=%s', (tokenId,))
                token = cur.fetchone()
                if (token is None):
                    msg = 'No token with supplied id.'
                    log(msg.replace('id.','id: %d.' % tokenId))
                    return dict(msg=msg, statusCode=400)
                else:
                    token = token[0] # fetchone() returns tuple

                # save recordings to recordings/sessionId/filename
                sessionPath = os.path.join(RECORDINGS_ROOT, 'session_'+str(sessionId))
                if not os.path.exists(sessionPath):
                    os.mkdir(sessionPath)
                
                recName = filename(speakerName) + '_' + filename(rec.filename)
                wavePath = os.path.join(sessionPath, recName)
                # rec is a werkzeug FileStorage object
                rec.save(wavePath)
                # save additional metadata to text file with same name as recording
                # open with codecs to avoid encoding issues.
                # right now, only save the token
                with open(wavePath.replace('.wav','.txt'), mode='w', encoding='utf8') as f:
                    f.write(token)

                # insert recording data into database
                cur.execute('INSERT INTO recording (tokenId, speakerId, sessionId, rel_path) \
                             VALUES (%s, %s, %s, %s)', 
                            (tokenId, speakerId, sessionId, wavePath))

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

        return dict(msg='{"sessionId":' + str(sessionId) + '}', statusCode=200)

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
        
    # gets *ALL* tokens from the database and returns them in a nice json format.
    # look at format in the client-server API
    # or it's: [{"id":id1, "token":token1}, {"id":id2, "token":token2}, ...]
    # returns [] on failure
    def getTokensAll(self):
        tokens = []
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT id, inputToken FROM token')
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
