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

from util import log

app = Flask(__name__)

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
        log('GET success baby')
    if request.method == 'POST':
        log('Form: ' + str(request.form) + '\nFiles: ' + str(request.files) + '\n')
        log('Headers: ' + str(request.headers))

        if 'json' in request.form:
            jsonData = request.form['json']
        else:
            log('No metadata found, aborting.')
            return 'asd'

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

        try:
            result = dbHandler.processSessionData(jsonData, recordings)
            log(result)
        # these error excepts are ONLY for debug right now
        except TypeError as e:
            log('error: ' + str(e) + '\n' + str(jsonData))
        except KeyError as e:
            log('error: ' + str(e) + '\n' + str(jsonData))
        except ValueError as e:
            log('error: ' + str(e) + '\n' + str(jsonData))

    return ''

@app.route('/submit/gettokens/<int:numTokens>', methods=['GET'])
def submit_gettokens(numTokens):
    response = ''

    if request.method == 'GET':
        response += str(dbHandler.getTokens(numTokens))

    return response

if __name__ == '__main__':
    app.run(debug=True)