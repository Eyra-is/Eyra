from flask import Flask, request, Response
#from flask.ext.cors import CORS
import json

from db_handler import DbHandler
from auth_handler import AuthHandler
from qc.qc_handler import QcHandler
#from qc.celery_handler import CeleryHandler

from util import log

app = Flask(__name__)

dbHandler = DbHandler(app)
authHandler = AuthHandler(app) # sets up /auth/login @app.route and @login_required()

from qc.celery_handler import add, qcProcessSession

#celeryHandler = CeleryHandler(app)
# important that this is set up before calling QcHandler
# this is pretty ugly though, it's not a config variable.
#   just needed a way to use this variable in all the handlers.
app.config['CELERY_QC_PROCESS_FN'] = qcProcessSession
app.config['CELERY_ADD'] = add
qcHandler = QcHandler(app)
# need the actual celery function/class to start the celery worker from cli
# now we can call it as app.celery
#celery = celeryHandler.getCelery()

# allow pretty much everything, this will be removed in production! since we will serve
#   the backend and frontend on the same origin/domain
# cors = CORS(app,    resources=r'/*', 
#                     allow_headers='*', 
#                     origins='*',
#                     methods='GET, POST, OPTIONS')

# SUBMISSION ROUTES

@app.route('/submit/general/<method>', methods=['POST'])
@authHandler.login_required()
def submit_general(method):
    """
    supports everything in the client-server API
    right now, /submit/general/{device,instuctor}
    
    requires sender to be authenticated with JWT, see auth_handler.py 
    remove @authHandler.login_required() if you don't want that
    """
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
            #log('Data: ' + str(request.form) + '\n')

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
        #log(msg)
        return msg, 200
    if request.method == 'POST':
        #log('Form: ' + str(request.form) + '\nFiles: ' + str(request.files) + '\n')
        #log('Headers: ' + str(request.headers))

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
                #log('Got file: ' + str(request.files[key]))
            else:
                #log('No more recordings.')
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
            #log('Got tokens from db: ' + response)
            return response, 200
        else:
            msg = 'Failed getting tokens from database.'
            log(msg)
            return msg, 500

    return 'Unexpected error.', 500

@app.route('/submit/gettokens/all', methods=['GET'])
def submit_gettokens_all():
    if request.method == 'GET':
        response = ''
        tokens = dbHandler.getTokensAll()
        if len(tokens) > 0:
            response += json.dumps(tokens)
            log('Got tokens from db: ' + response)
            return response, 200
        else:
            msg = 'Failed getting tokens from database.'
            log(msg)
            return msg, 500

    return 'Unexpected error.', 500

# QC ROUTES

@app.route('/qc/report/session/<int:sessionId>', methods=['GET'])
def qc_report(sessionId):
    """Get a QC report

    Returned JSON if the QC report is not available, but is being
    processed:

        {"sessionId": ...,
         "status": "started"}

    Returned JSON definition if no QC module is active:

        {"sessionId": ...,
         "status": "inactive"}

    Returned JSON definition:

        {"sessionId": ...,
         "status": "processing",
         "totalStats": {"accuracy": [0.0;1.0]"},
         "perRecordingStats": [{"recordingId": ...,
                                "stats": {"accuracy": [0.0;1.0]},
                                ... TBD ...}]
        }

    """
    if request.method == 'GET':
        # TODO: handle non-existent session ids -> 404
        qcReport = qcHandler.getReport(sessionId)
        return json.dumps(qcReport), 200

    return 'Unexpected error.', 500

if __name__ == '__main__':
    app.run(debug=True)
