# **************************************************************************************** #

#                                         TODO                                             #

# Reevaluate submit_session route format, e.g. have just a /submit and look at type through json data
# Add code to calculate duration of wav files if needed

# Make CORS more secure, e.g. not origins='*' but from a specific domain only.
# WARNING Because of the abstraction in db_handler, the keys have to be put manually into the 
#   string without being semi prepared, which means at least the keys of the data should be
#   somewhat sanitized
# Add functionality frontend and backend, to save the speaker and device ID's returned from server
#   and thusly be able to identify devices even if no IMEI is present and to avoid speaker ambiguities
# Generalize even further, generalize the 'if in database, return that id, otherwise insert'

# ***************************************************************************************** #

from flask import Flask, request
from db_handler import DbHandler
from flask.ext.cors import CORS
import json

from util import log

app = Flask(__name__)

dbHandler = DbHandler(app)

cors = CORS(app,    resources=r'/submit/*', 
                    allow_headers='Content-Type', # 'Content-Type, *'
                    origins='*',
                    methods='GET, POST, OPTIONS')

# supports everything in the client-server API
# right now, /submit/general/{device,instuctor,speaker}
@app.route('/submit/general/<method>', methods=['POST'])
def submit_general(method):
    processingFunction = None
    if method=='device':
        processingFunction = dbHandler.processDeviceData
    elif method=='instructor':
        processingFunction = dbHandler.processInstructorData
    elif method=='speaker':
        processingFunction = dbHandler.processSpeakerData

    if method is not None:
        data = None
        if request.method == 'POST':
            log('Data: ' + str(request.form) + '\n')

            if 'json' in request.form:
                data = request.form['json']
            else:
                msg = 'No %s data found in submission, aborting.' % method
                log(msg)
                return msg, 400

            result = processingFunction(data)
            return result['msg'], result['statusCode']

        return 'Unexpected error.', 500

    return 'Not a valid submission method url.', 404

@app.route('/submit/session', methods=['GET', 'POST'])
def submit_session():
    sessionData = None
    recordings = []
    if request.method == 'GET':
        msg = 'GET success baby'
        log(msg)
        return msg, 200
    if request.method == 'POST':
        log('Form: ' + str(request.form) + '\nFiles: ' + str(request.files) + '\n')
        log('Headers: ' + str(request.headers))

        if 'json' in request.form:
            sessionData = request.form['json']
        else:
            msg = 'No metadata found, aborting.'
            log(msg)
            return msg, 400

        i = 0
        while True:
            key = 'rec'+str(i)
            if key in request.files:
                recordings.append(request.files[key])
                log('Got file: ' + str(request.files[key]))
            else:
                log('No more recordings.')
                break
            i += 1

        if i==0:
            msg = 'No recordings received, aborting.'
            log(msg)
            return msg, 400

        result = dbHandler.processSessionData(sessionData, recordings)
        return result['msg'], result['statusCode']

    return 'Unexpected error.', 500

@app.route('/submit/gettokens/<int:numTokens>', methods=['GET'])
def submit_gettokens(numTokens):
    if request.method == 'GET':
        response = ''
        tokens = dbHandler.getTokens(numTokens)
        if len(tokens) > 0:
            response += json.dumps(tokens)
            log('Got tokens from db: ' + response)
            return response, 200
        else:
            msg = 'Failed getting tokens from database.'
            log(msg)
            return msg, 500

    return 'Unexpected error.', 500

if __name__ == '__main__':
    app.run(debug=True)