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
# Remove Flask-MySQLdb and simply use MySQLdb, no need for the flask extension (low usage on github) I think
# REMEMBER TO CHANGE SECRET KEY IN AUTH HANDLER FOR GITHUB RELEASE/PRODUCTION

# ***************************************************************************************** #

from flask import Flask, request, Response
from flask.ext.cors import CORS
import json

from db_handler import DbHandler
from auth_handler import AuthHandler

from util import log

app = Flask(__name__)

dbHandler = DbHandler(app)
authHandler = AuthHandler(app) # sets up /auth/login @app.route and @login_required()

# allow pretty much everything, this will be removed in production! since we will serve
#   the backend and frontend on the same origin/domain
cors = CORS(app,    resources=r'/*', 
                    allow_headers='*', 
                    origins='*',
                    methods='GET, POST, OPTIONS')

# SUBMISSION ROUTES

# supports everything in the client-server API
# right now, /submit/general/{device,instuctor}
#
# requires sender to be authenticated with JWT, see auth_handler.py 
# remove @authHandler.login_required() if you don't want that
@app.route('/submit/general/<method>', methods=['POST'])
@authHandler.login_required()
def submit_general(method):
    validMethod = False
    processingFunction = None
    if method=='device':
        processingFunction = dbHandler.processDeviceData
        validMethod = True
    elif method=='instructor':
        processingFunction = dbHandler.processInstructorData
        validMethod = True
    # not used currently, speaker data is sent with each session
    #elif method=='speaker':
    #    processingFunction = dbHandler.processSpeakerData
    #    validMethod = True

    if method is not None and validMethod:
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