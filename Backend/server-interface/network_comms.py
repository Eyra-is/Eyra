# **************************************************************************************** #

#                                         TODO                                             #

# Reevaluate submit_session route format, e.g. have just a /submit and look at type through json data
# Add try catch for production code, right now, better to skip it for the DEBUGGER messages
# Think about if we shouldn't just allow unlimited recordings processed, they are uploaded anyway
# Add code to calculate duration of wav files if needed from flask import Flask, request

# Make CORS more secure, e.g. not origins='*' but from a specific domain only.

# ***************************************************************************************** #

from flask import Flask, request
from db_handler import DbHandler
from flask.ext.cors import CORS

app = Flask(__name__)

dbHandler = DbHandler(app)

cors = CORS(app,    resources=r'/submit/*', 
                    allow_headers='Content-Type', 
                    origins='*', 
                    methods='GET, POST, OPTIONS')

@app.route('/submit/session', methods=['GET', 'POST'])
def submit_session():
    MAX_RECORDINGS = 50 # maximum recordings per session 
    response = '' # debug

    jsonData = None
    recordings = []
    if request.method == 'GET':
        response += 'GET success baby'
    if request.method == 'POST':
        response += 'Form: ' + str(request.form) + '\nFiles: ' + str(request.files) + '\n\n'
        response += 'Request: ' + str(request) + '\n'
        #response += request.params + '\n'
        response += 'Url: ' + request.url + '\n'
        response += 'Data: ' + str(request.data) + '\n'
        response += 'Json: ' + str(request.json) + '\n'
        response += 'Headers: ' + str(request.headers) + '\n'
        response += 'Stream: ' + str(request.stream) + '\n'

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

        try:
            response += dbHandler.processSessionData(jsonData, recordings)
        # these error excepts are ONLY for debug right now
        except TypeError as e:
            response += 'error: ' + str(e) + '\n'
            response += str(jsonData)
        except KeyError as e:
            response += 'error: ' + str(e) + '\n'
            response += str(jsonData)
        except ValueError as e:
            response += 'error: ' + str(e) + '\n'
            response += str(jsonData)

    return response

@app.route('/submit/gettokens/<int:numTokens>', methods=['GET'])
def submit_gettokens(numTokens):
    response = ''

    if request.method == 'GET':
        response += str(dbHandler.getTokens(numTokens))

    return response

if __name__ == '__main__':
    app.run(debug=True)