# **************************************************************************************** #

#                                         TODO                                             #

# Reevaluate submit_session route format, e.g. have just a /submit and look at type through json data
# Add try catch for production code, right now, better to skip it for the DEBUGGER messages
# Think about if we shouldn't just allow unlimited recordings processed, they are uploaded anyway
# Add code to calculate duration of wav files if needed from flask import Flask, request

# ***************************************************************************************** #

from flask import Flask, request
from db_handler import DbHandler

app = Flask(__name__)

dbHandler = DbHandler(app)


@app.route('/submit/session', methods=['POST'])
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

        response += dbHandler.processSessionData(jsonData, recordings)

    return response

if __name__ == '__main__':
    app.run(debug=True)