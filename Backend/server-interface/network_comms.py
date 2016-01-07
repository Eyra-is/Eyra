# **************************************************************************************** #

#                                         TODO                                             #

# Reevaluate submit_session route format, e.g. have just a /submit and look at type through json data
# Add try catch for production code, right now, better to skip it for the DEBUGGER messages
# Add code to calculate duration of wav files if needed

# Make CORS more secure, e.g. not origins='*' but from a specific domain only.

# ***************************************************************************************** #

from flask import Flask, request
from db_handler import DbHandler
from flask.ext.cors import CORS
import json

from util import log



app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024 # limit at 2 GB

dbHandler = DbHandler(app)

cors = CORS(app,    resources=r'/submit/*', 
                    allow_headers='Content-Type', # 'Content-Type, *'
                    origins='*',
                    methods='GET, POST, OPTIONS')

@app.route('/submit/session', methods=['GET', 'POST'])
def submit_session():
    jsonData = None
    recordings = []
    if request.method == 'GET':
        msg = 'GET success baby'
        log(msg)
        return msg, 200
    if request.method == 'POST':
        log('Form: ' + str(request.form) + '\nFiles: ' + str(request.files) + '\n')
        log('Headers: ' + str(request.headers))

        if 'json' in request.form:
            jsonData = request.form['json']
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

        result = dbHandler.processSessionData(jsonData, recordings)
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