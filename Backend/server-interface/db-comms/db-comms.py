# **************************************************************************************** #

#                                         TODO                                             #

# Reevaluate submit_session route format, e.g. have just a /submit and look at type through json data
# Add try catch for production code, right now, better to skip it for the DEBUGGER messages
# Think about if we shouldn't just allow unlimited recordings processed, they are uploaded anyway
# Add code to calculate duration of wav files if neededfrom flask import Flask, request

# ***************************************************************************************** #

from flask import Flask, request
from flask.ext.mysqldb import MySQL
import json
import os # for mkdir

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'default'
app.config['MYSQL_DB']   = 'recordings_master'

mysql = MySQL(app)

@app.route('/submit/session', methods=['GET','POST'])
def submit_session():
    MAX_RECORDINGS = 50 # maximum recordings per session 
    response = '' # debug

    jsonData = None
    recordings = []
    if request.method == 'POST':
        response += 'Form: ' + str(request.form) + '\nFiles: ' + str(request.files) + '\n\n'

        if 'json' in request.form:
            jsonData = request.form['json']

        for i in range(MAX_RECORDINGS):
            key = 'rec'+str(i)
            if key in request.files:
                recordings.append(request.files[key])
                response += 'Got file: ' + str(request.files[key]) + '\n'
            else:
                response += 'No more recordings.\n'
                break
            if i == MAX_RECORDINGS-1:
                response += 'Reached recording count limit, not processing more recordings.\n'
                break

        response += processSessionData(jsonData, recordings)

    return response


# jsonData = look at format in the client-server API
# recordings = an array of file objects representing the submitted recordings
def processSessionData(jsonData, recordings):
    RECORDINGS_ROOT = 'recordings' # root path to recordings
    jsonDecoded = None
    sessionId = None
    output = ''

    jsonDecoded = json.loads(jsonData)
    output += str(jsonDecoded)
    if jsonDecoded['type'] == 'session':
        jsonDecoded = jsonDecoded['data']

    # insert json data into our database
    #
    # start with the session table
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO session (speakerId, instructorId, deviceId, location, start, end, comments) \
                 VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                (jsonDecoded['speakerId'], jsonDecoded['instructorId'], jsonDecoded['deviceId'],
                 jsonDecoded['location'], jsonDecoded['start'], jsonDecoded['end'], jsonDecoded['comments']))
    # get the newly auto generated session.id 
    cur.execute('SELECT id FROM session WHERE \
                 speakerId=%s AND instructorId=%s AND deviceId=%s AND location=%s AND start=%s AND end=%s',
                (jsonDecoded['speakerId'], jsonDecoded['instructorId'], jsonDecoded['deviceId'],
                 jsonDecoded['location'], jsonDecoded['start'], jsonDecoded['end']))
    sessionId = cur.fetchone()[0] # not sure why fetchone returns a tuple

    # now populate recordings table
    #
    # make sure path to recordings exists
    if not os.path.exists(RECORDINGS_ROOT):
        os.mkdir(RECORDINGS_ROOT)
    for rec in recordings:
        # save recordings to recordings/sessionId/filename
        sessionPath = os.path.join(RECORDINGS_ROOT, str(sessionId))
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
    mysql.connection.commit()

    return 'Successful process of session data.\n'

if __name__ == '__main__':
    app.run(debug=True)